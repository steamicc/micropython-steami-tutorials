#!/usr/bin/env python3
"""
Board validation for steami_screen tutorials.

For each tutorial, runs the drawing code on the real STeaMi hardware via
mpremote, dumps the GS4_HMSB framebuffer, decodes it to PNG, and compares
the board render against the simulator PNG and the SVG reference.

This lets you verify that steami_screen behaves correctly on real hardware.

Prerequisites:
    pip install mpremote Pillow numpy scikit-image cairosvg
    The board must be connected via USB.

Usage:
    python tools/board_validate.py                    # validate all tutorials
    python tools/board_validate.py 04_circular_gauge  # one tutorial
    python tools/board_validate.py --upload-libs      # upload lib/ first
    python tools/board_validate.py --threshold 0.60   # custom threshold

Note on expected scores:
    Board vs sim: ~0.60–0.80 (board uses 8x8 pixel font, sim uses TrueType)
    Board vs ref: ~0.55–0.75
    These differences are normal and expected — the board score shows the real
    rendering gap between the hardware and the simulation.
"""

import argparse
import importlib.util
import inspect
import os
import subprocess
import sys
import tempfile
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCKUPS_DIR = os.path.join(ROOT, "docs", "mockups")
TUTORIALS_DIR = os.path.join(ROOT, "tutorials")
LIB_DIR = os.path.join(ROOT, "lib")

# Add lib/ to path so we can load screenshot.py modules that import steami_screen
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

DEFAULT_THRESHOLD = 0.50

# Board runner template — injected with the draw() body, runs via mpremote
_BOARD_TEMPLATE = """\
import sys
sys.path.append("/lib")
import ssd1327
from machine import SPI, Pin
from steami_ssd1327 import SSD1327Display
from steami_screen import (
    Screen, BLACK, DARK, GRAY, LIGHT, WHITE, GREEN, RED, YELLOW, BLUE
)

spi = SPI(1)
dc  = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs  = Pin("CS_DISPLAY")
raw = ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs)
display = SSD1327Display(raw)
screen = Screen(display)

{draw_body}

# --- Framebuffer dump (GS4_HMSB, 8192 bytes) ---
try:
    buf = bytes(raw.buf)
except AttributeError:
    try:
        buf = bytes(raw.buffer)
    except AttributeError:
        import framebuf as _fb
        _tmp = bytearray(8192)
        _fb.FrameBuffer(_tmp, 128, 128, _fb.GS4_HMSB).blit(raw.framebuf, 0, 0)
        buf = bytes(_tmp)
print("FB:" + buf.hex())
"""


# ---------------------------------------------------------------------------
# Tutorial discovery
# ---------------------------------------------------------------------------

def find_tutorials():
    """Discover all tutorials that have a screenshot.py with a draw() function."""
    tutorials = []
    if not os.path.isdir(TUTORIALS_DIR):
        return tutorials
    for name in sorted(os.listdir(TUTORIALS_DIR)):
        screenshot = os.path.join(TUTORIALS_DIR, name, "screenshot.py")
        if os.path.isfile(screenshot):
            tutorials.append(name)
    return tutorials


# ---------------------------------------------------------------------------
# Draw body extraction
# ---------------------------------------------------------------------------

def load_draw_body(screenshot_path):
    """Load screenshot.py and extract the body of its draw() function.

    Returns the dedented function body as a string (without the def line).
    """
    spec = importlib.util.spec_from_file_location("_scr", screenshot_path)
    mod = importlib.util.module_from_spec(spec)
    # Prevent __name__ == "__main__" block from executing
    mod.__name__ = "_scr"
    spec.loader.exec_module(mod)

    if not hasattr(mod, "draw"):
        raise AttributeError(
            f"screenshot.py has no draw() function: {screenshot_path}\n"
            "Run refactoring first (see tools/board_validate.py docs)."
        )

    src = inspect.getsource(mod.draw)
    lines = src.splitlines()
    # Skip first line ("def draw(screen):") and dedent the body
    body = textwrap.dedent("\n".join(lines[1:]))
    return body.strip()


# ---------------------------------------------------------------------------
# Board script construction and execution
# ---------------------------------------------------------------------------

def build_board_script(draw_body):
    """Build the self-contained MicroPython script to run on the board."""
    return _BOARD_TEMPLATE.format(draw_body=draw_body)


def run_on_board(script):
    """Write script to a temp file, run via mpremote, return (hex_data, error)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, prefix="steami_cap_"
    ) as f:
        f.write(script)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["mpremote", "connect", "auto", "run", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None, result.stderr.strip() or result.stdout.strip()

        for line in result.stdout.splitlines():
            if line.startswith("FB:"):
                return line[3:].strip(), None

        # No FB: line found — show what the board printed for debugging
        output = result.stdout.strip()
        return None, f"No 'FB:' line in board output:\n{output}"

    except subprocess.TimeoutExpired:
        return None, "mpremote timed out (30s)"
    except FileNotFoundError:
        return None, "mpremote not found — install with: pip install mpremote"
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# GS4_HMSB framebuffer decoding
# ---------------------------------------------------------------------------

def gs4_hmsb_to_image(hex_data, width=128, height=128):
    """Decode a GS4_HMSB hex dump to a PIL RGB image.

    GS4_HMSB: 4 bits per pixel, high nibble = left pixel.
    Each byte encodes two adjacent pixels.
    """
    from PIL import Image
    import numpy as np

    raw = bytes.fromhex(hex_data)
    if len(raw) != width * height // 2:
        raise ValueError(
            f"Expected {width * height // 2} bytes, got {len(raw)}"
        )

    pixels = []
    for byte in raw:
        pixels.append(((byte >> 4) & 0xF) * 17)  # high nibble → 0-255
        pixels.append((byte & 0xF) * 17)           # low nibble  → 0-255

    arr = np.array(pixels, dtype=np.uint8).reshape(height, width)
    return Image.fromarray(arr, "L").convert("RGB")


# ---------------------------------------------------------------------------
# Image comparison (reused from validate.py logic)
# ---------------------------------------------------------------------------

def structural_similarity(img_path_a, img_path_b):
    """Compute SSIM or pixel-MAE similarity between two image files."""
    try:
        from PIL import Image
        import numpy as np
        from skimage.metrics import structural_similarity as ssim

        img_a = np.array(Image.open(img_path_a).convert("RGB"))
        img_b = np.array(Image.open(img_path_b).convert("RGB"))

        if img_a.shape != img_b.shape:
            from PIL import Image as _I
            min_h = min(img_a.shape[0], img_b.shape[0])
            min_w = min(img_a.shape[1], img_b.shape[1])
            img_a = np.array(_I.open(img_path_a).convert("RGB").resize((min_w, min_h)))
            img_b = np.array(_I.open(img_path_b).convert("RGB").resize((min_w, min_h)))

        score = ssim(img_a, img_b, channel_axis=-1)
        return score, "SSIM"
    except ImportError:
        return _pixel_similarity(img_path_a, img_path_b), "pixel-MAE"


def _pixel_similarity(img_path_a, img_path_b):
    from PIL import Image
    img_a = Image.open(img_path_a).convert("RGB")
    img_b = Image.open(img_path_b).convert("RGB")
    size = (min(img_a.width, img_b.width), min(img_a.height, img_b.height))
    img_a = img_a.resize(size)
    img_b = img_b.resize(size)
    pa = list(img_a.getdata())
    pb = list(img_b.getdata())
    total = sum(abs(a[i] - b[i]) for a, b in zip(pa, pb) for i in range(3))
    return 1.0 - total / (255 * 3 * len(pa))


def generate_diff_image(img_path_a, img_path_b, out_path):
    """Save an amplified difference image (×5) between two files."""
    from PIL import Image
    img_a = Image.open(img_path_a).convert("RGB")
    img_b = Image.open(img_path_b).convert("RGB")
    size = (min(img_a.width, img_b.width), min(img_a.height, img_b.height))
    img_a = img_a.resize(size)
    img_b = img_b.resize(size)
    pa, pb = list(img_a.getdata()), list(img_b.getdata())
    diff = [
        tuple(min(255, abs(a[i] - b[i]) * 5) for i in range(3))
        for a, b in zip(pa, pb)
    ]
    diff_img = Image.new("RGB", size)
    diff_img.putdata(diff)
    diff_img.save(out_path)


# ---------------------------------------------------------------------------
# Optional: upload library files to the board
# ---------------------------------------------------------------------------

def upload_libs():
    """Upload steami_screen library files to /lib on the board."""
    libs = ["steami_screen.py", "steami_ssd1327.py", "steami_colors.py"]
    for lib in libs:
        src = os.path.join(LIB_DIR, lib)
        dst = f":lib/{lib}"
        print(f"  Uploading {lib} → {dst}")
        result = subprocess.run(
            ["mpremote", "connect", "auto", "fs", "cp", src, dst],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}")
            return False
    return True


# ---------------------------------------------------------------------------
# Per-tutorial validation
# ---------------------------------------------------------------------------

def validate_tutorial(tutorial_name, threshold):
    """Capture board render and compare with sim + ref. Returns True if PASS."""
    print(f"\n--- {tutorial_name} ---")

    screenshot_path = os.path.join(TUTORIALS_DIR, tutorial_name, "screenshot.py")
    if not os.path.isfile(screenshot_path):
        print("  ERROR: no screenshot.py found")
        return False

    # Step 1: Extract draw() body
    print("  [1/4] Extracting draw() from screenshot.py...")
    try:
        draw_body = load_draw_body(screenshot_path)
    except AttributeError as e:
        print(f"  ERROR: {e}")
        return False

    # Step 2: Run on board and get framebuffer
    print("  [2/4] Running on board (mpremote)...")
    script = build_board_script(draw_body)
    hex_data, err = run_on_board(script)
    if hex_data is None:
        print(f"  ERROR: {err}")
        return False
    print(f"  Received {len(hex_data)//2} bytes from board")

    # Step 3: Decode and save board PNG
    print("  [3/4] Decoding framebuffer...")
    try:
        board_img = gs4_hmsb_to_image(hex_data)
    except (ValueError, Exception) as e:
        print(f"  ERROR decoding framebuffer: {e}")
        return False

    board_png = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_board.png")
    board_img.save(board_png)
    print(f"  Saved: {board_png}")

    # Step 4: Compare
    print("  [4/4] Comparing...")
    results = {}

    sim_png = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_sim.png")
    if os.path.isfile(sim_png):
        score, method = structural_similarity(board_png, sim_png)
        status = "PASS" if score >= threshold else "FAIL"
        results["board_vs_sim"] = (score, method, status)
        diff_path = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_board_diff.png")
        generate_diff_image(board_png, sim_png, diff_path)
        print(f"  board vs sim : {score:.4f} ({method}) — {status}")
    else:
        print("  board vs sim : SKIP (no sim PNG, run validate.py first)")

    ref_png = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_ref.png")
    if os.path.isfile(ref_png):
        score, method = structural_similarity(board_png, ref_png)
        status = "PASS" if score >= threshold else "FAIL"
        results["board_vs_ref"] = (score, method, status)
        print(f"  board vs ref : {score:.4f} ({method}) — {status}")
    else:
        print("  board vs ref : SKIP (no ref PNG, run validate.py first)")

    # Overall: pass if at least one comparison passes
    if not results:
        print("  No comparisons available (run validate.py first)")
        return True  # board capture itself succeeded

    return any(v[2] == "PASS" for v in results.values())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate steami_screen tutorials on real hardware"
    )
    parser.add_argument(
        "tutorials", nargs="*",
        help="Tutorial names to validate (default: all)"
    )
    parser.add_argument(
        "--upload-libs", action="store_true",
        help="Upload lib/ files to the board before validating"
    )
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD,
        help=f"SSIM threshold for board comparisons (default: {DEFAULT_THRESHOLD})"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available tutorials and exit"
    )
    args = parser.parse_args()

    all_tutorials = find_tutorials()

    if args.list:
        print("Available tutorials:")
        for t in all_tutorials:
            print(f"  {t}")
        return

    tutorials = args.tutorials if args.tutorials else all_tutorials
    if not tutorials:
        print("No tutorials found.")
        return

    # Optional library upload
    if args.upload_libs:
        print("Uploading library files to board...")
        if not upload_libs():
            print("ERROR: library upload failed, aborting.")
            sys.exit(1)
        print("Libraries uploaded.")

    print(
        f"\nBoard validation: {len(tutorials)} tutorial(s), "
        f"threshold={args.threshold}"
    )
    print("Note: board vs sim scores ~0.60–0.80 are normal (font differences)")

    results = {}
    for name in tutorials:
        if name not in all_tutorials:
            print(f"\nWARNING: tutorial '{name}' not found, skipping")
            continue
        results[name] = validate_tutorial(name, args.threshold)

    # Summary
    print("\n" + "=" * 40)
    print("BOARD VALIDATION SUMMARY")
    print("=" * 40)
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    for name, ok in results.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n{passed} passed, {failed} failed out of {len(results)}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
