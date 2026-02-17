#!/usr/bin/env python3
"""
Validation pipeline for steami_screen tutorials.

For each tutorial:
1. Runs screenshot.py to produce a simulator PNG
2. Rasterizes the SVG reference mockup to PNG (same size)
3. Computes a similarity score between the two
4. Reports PASS/FAIL based on a configurable threshold

Dependencies:
    pip install Pillow cairosvg

Usage:
    python validate.py                   # validate all tutorials
    python validate.py 01_temperature    # validate one tutorial
    python validate.py --threshold 0.6   # custom similarity threshold
"""

import os
import sys
import subprocess
import argparse
import importlib

ROOT = os.path.dirname(os.path.abspath(__file__))
MOCKUPS_DIR = os.path.join(ROOT, "docs", "mockups")
TUTORIALS_DIR = os.path.join(ROOT, "tutorials")

# Default similarity threshold (0.0 = totally different, 1.0 = identical)
DEFAULT_THRESHOLD = 0.95


def find_tutorials():
    """Discover all tutorials that have a screenshot.py."""
    tutorials = []
    if not os.path.isdir(TUTORIALS_DIR):
        return tutorials
    for name in sorted(os.listdir(TUTORIALS_DIR)):
        screenshot = os.path.join(TUTORIALS_DIR, name, "screenshot.py")
        if os.path.isfile(screenshot):
            tutorials.append(name)
    return tutorials


def run_screenshot(tutorial_name):
    """Run a tutorial's screenshot.py and return the output PNG path."""
    script = os.path.join(TUTORIALS_DIR, tutorial_name, "screenshot.py")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode != 0:
        print(f"  ERROR running screenshot.py:\n{result.stderr}")
        return None

    # Expected output path
    png_path = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_sim.png")
    if os.path.isfile(png_path):
        return png_path
    print(f"  ERROR: expected output not found: {png_path}")
    return None


def rasterize_svg(tutorial_name, target_size):
    """Rasterize the SVG mockup reference to PNG at the given size."""
    svg_path = os.path.join(MOCKUPS_DIR, f"{tutorial_name}.svg")
    if not os.path.isfile(svg_path):
        print(f"  WARNING: no SVG reference found: {svg_path}")
        return None

    png_path = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_ref.png")

    try:
        import cairosvg
        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            output_width=target_size,
            output_height=target_size,
            background_color="black"
        )
        return png_path
    except ImportError:
        print("  WARNING: cairosvg not installed, skipping SVG rasterization")
        print("  Install with: pip install cairosvg")
        return None


def compute_similarity(img_path_a, img_path_b):
    """Compute a normalized similarity score between two images.

    Uses a histogram-based comparison (no scikit-image dependency).
    Returns a float between 0.0 (totally different) and 1.0 (identical).
    """
    from PIL import Image

    img_a = Image.open(img_path_a).convert("L")
    img_b = Image.open(img_path_b).convert("L")

    # Resize to same dimensions
    size = (min(img_a.width, img_b.width), min(img_a.height, img_b.height))
    img_a = img_a.resize(size)
    img_b = img_b.resize(size)

    # Pixel-level comparison: mean absolute error normalized to [0,1]
    pixels_a = list(img_a.getdata())
    pixels_b = list(img_b.getdata())

    total_diff = sum(abs(a - b) for a, b in zip(pixels_a, pixels_b))
    max_diff = 255 * len(pixels_a)

    similarity = 1.0 - (total_diff / max_diff)
    return similarity


def structural_similarity(img_path_a, img_path_b):
    """Try SSIM if scikit-image is available, else fall back to pixel comparison."""
    try:
        from PIL import Image
        import numpy as np
        from skimage.metrics import structural_similarity as ssim

        img_a = np.array(Image.open(img_path_a).convert("L"))
        img_b = np.array(Image.open(img_path_b).convert("L"))

        # Resize if needed
        if img_a.shape != img_b.shape:
            min_h = min(img_a.shape[0], img_b.shape[0])
            min_w = min(img_a.shape[1], img_b.shape[1])
            img_a = np.array(Image.open(img_path_a).convert("L").resize((min_w, min_h)))
            img_b = np.array(Image.open(img_path_b).convert("L").resize((min_w, min_h)))

        score = ssim(img_a, img_b)
        return score, "SSIM"
    except ImportError:
        score = compute_similarity(img_path_a, img_path_b)
        return score, "pixel-MAE"


def validate_tutorial(tutorial_name, threshold):
    """Validate a single tutorial. Returns True if PASS."""
    print(f"\n--- {tutorial_name} ---")

    # Step 1: Generate simulator screenshot
    print("  [1/3] Running screenshot.py...")
    sim_png = run_screenshot(tutorial_name)
    if sim_png is None:
        return False

    from PIL import Image
    sim_img = Image.open(sim_png)
    target_size = sim_img.width
    print(f"  Simulator output: {sim_png} ({sim_img.width}x{sim_img.height})")

    # Step 2: Rasterize SVG reference
    print("  [2/3] Rasterizing SVG reference...")
    ref_png = rasterize_svg(tutorial_name, target_size)
    if ref_png is None:
        print("  SKIP (no reference to compare)")
        return True  # don't fail if no SVG yet

    # Step 3: Compare
    print("  [3/3] Comparing images...")
    score, method = structural_similarity(sim_png, ref_png)
    status = "PASS" if score >= threshold else "FAIL"
    print(f"  Score: {score:.4f} ({method}) — threshold: {threshold} — {status}")

    return score >= threshold


def main():
    parser = argparse.ArgumentParser(description="Validate steami_screen tutorials")
    parser.add_argument("tutorials", nargs="*", help="Tutorial names to validate (default: all)")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help=f"Similarity threshold (default: {DEFAULT_THRESHOLD})")
    parser.add_argument("--list", action="store_true", help="List available tutorials")
    args = parser.parse_args()

    all_tutorials = find_tutorials()

    if args.list:
        print("Available tutorials:")
        for t in all_tutorials:
            svg = os.path.join(MOCKUPS_DIR, f"{t}.svg")
            has_svg = "SVG" if os.path.isfile(svg) else "   "
            print(f"  [{has_svg}] {t}")
        return

    tutorials = args.tutorials if args.tutorials else all_tutorials
    if not tutorials:
        print("No tutorials found. Create tutorials with screenshot.py in tutorials/*/")
        return

    print(f"Validating {len(tutorials)} tutorial(s), threshold={args.threshold}")

    results = {}
    for name in tutorials:
        if name not in all_tutorials:
            print(f"\nWARNING: tutorial '{name}' not found, skipping")
            continue
        results[name] = validate_tutorial(name, args.threshold)

    # Summary
    print("\n" + "=" * 40)
    print("VALIDATION SUMMARY")
    print("=" * 40)
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n{passed} passed, {failed} failed out of {len(results)}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
