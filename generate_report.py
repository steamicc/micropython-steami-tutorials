#!/usr/bin/env python3
"""
Generate docs/mockups/README.md — a visual report of all steami_screen tutorials.

For each tutorial:
- Runs screenshot.py to refresh the simulator PNG
- Rasterizes the SVG reference mockup
- Computes SSIM similarity score
- Generates a 2-column gallery in Markdown (HTML table)

Usage:
    python generate_report.py

Dependencies:
    pip install Pillow cairosvg scikit-image numpy
"""

import ast
import os
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
MOCKUPS_DIR = os.path.join(ROOT, "docs", "mockups")
TUTORIALS_DIR = os.path.join(ROOT, "tutorials")
PYTHON = sys.executable
THRESHOLD_SSIM = 0.85


# ---------------------------------------------------------------------------
# Discovery and metadata
# ---------------------------------------------------------------------------

def find_tutorials():
    """Return sorted list of tutorial names that have a screenshot.py."""
    tutorials = []
    if not os.path.isdir(TUTORIALS_DIR):
        return tutorials
    for name in sorted(os.listdir(TUTORIALS_DIR)):
        path = os.path.join(TUTORIALS_DIR, name, "screenshot.py")
        if os.path.isfile(path):
            tutorials.append(name)
    return tutorials


def extract_metadata(tutorial_name):
    """Parse the METADATA dict from a tutorial's screenshot.py using ast."""
    path = os.path.join(TUTORIALS_DIR, tutorial_name, "screenshot.py")
    with open(path, encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "METADATA":
                        return ast.literal_eval(node.value)
    except Exception:
        pass
    return {"title": tutorial_name, "widget": "", "description": ""}


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

def run_screenshot(tutorial_name):
    """Run screenshot.py to refresh the simulator PNG. Returns True on success."""
    script = os.path.join(TUTORIALS_DIR, tutorial_name, "screenshot.py")
    result = subprocess.run(
        [PYTHON, script], capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode != 0:
        print(f"  WARNING: screenshot.py failed: {result.stderr[:200]}")
        return False
    return True


def rasterize_svg(tutorial_name, size=384):
    """Rasterize the SVG reference to PNG. Returns True on success."""
    svg_path = os.path.join(MOCKUPS_DIR, f"{tutorial_name}.svg")
    if not os.path.isfile(svg_path):
        return False
    ref_path = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_ref.png")
    try:
        import cairosvg
        cairosvg.svg2png(
            url=svg_path,
            write_to=ref_path,
            output_width=size,
            output_height=size,
            background_color="black",
        )
        return True
    except ImportError:
        print("  WARNING: cairosvg not installed, skipping SVG rasterization")
        return False


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_ssim(tutorial_name):
    """Compute SSIM between sim and ref PNGs. Returns float or None."""
    sim_path = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_sim.png")
    ref_path = os.path.join(MOCKUPS_DIR, f"{tutorial_name}_ref.png")
    if not (os.path.isfile(sim_path) and os.path.isfile(ref_path)):
        return None
    try:
        from PIL import Image
        import numpy as np
        from skimage.metrics import structural_similarity as ssim

        img_a = Image.open(sim_path).convert("RGB")
        img_b = Image.open(ref_path).convert("RGB")
        if img_a.size != img_b.size:
            w = min(img_a.width, img_b.width)
            h = min(img_a.height, img_b.height)
            img_a = img_a.resize((w, h))
            img_b = img_b.resize((w, h))
        return ssim(np.array(img_a), np.array(img_b), channel_axis=-1)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _card(name, meta, score, has_svg):
    """Return the HTML block for a single tutorial card."""
    title = meta.get("title", name)
    widget = meta.get("widget", "")
    description = meta.get("description", "")
    main_link = f"../../tutorials/{name}/main.py"

    lines = []
    lines.append("    <td align='center' valign='top' width='50%'>")
    lines.append(f"      <strong><a href='{main_link}'>{title}</a></strong><br><br>")

    if has_svg:
        lines.append(
            f"      <img src='{name}.svg' width='180' title='SVG reference'>&nbsp;"
            f"<img src='{name}_sim.png' width='180' title='Simulation'><br>"
        )
        lines.append("      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>")
    else:
        lines.append(f"      <img src='{name}_sim.png' width='180' title='Simulation'><br>")
        lines.append("      <sub>Simulation</sub><br>")

    lines.append(f"      <br><code>{widget}</code><br>")
    lines.append(f"      <sub>{description}</sub><br>")

    if score is not None:
        badge = "✅" if score >= THRESHOLD_SSIM else "❌"
        lines.append(f"      <sub>SSIM&nbsp;{score:.4f}&nbsp;{badge}</sub>")

    lines.append("    </td>")
    return "\n".join(lines)


def generate_report(tutorials, data):
    """Build the full README.md content string."""
    today = date.today().isoformat()
    passed = sum(1 for d in data.values() if d["score"] is not None and d["score"] >= THRESHOLD_SSIM)
    total_scored = sum(1 for d in data.values() if d["score"] is not None)

    lines = []
    lines.append("# steami\\_screen — Visual Report\n")
    lines.append(
        f"**{len(tutorials)} tutorials** · "
        f"**{passed}/{total_scored} PASS** (SSIM ≥ {THRESHOLD_SSIM}) · "
        f"Generated {today}\n"
    )
    lines.append(
        "Each card shows the SVG reference mockup alongside the Pillow simulation, "
        "with the SSIM similarity score.\n"
    )
    lines.append("")

    lines.append("<table>")
    for i in range(0, len(tutorials), 2):
        lines.append("  <tr>")
        for j in range(2):
            if i + j < len(tutorials):
                name = tutorials[i + j]
                d = data[name]
                lines.append(_card(name, d["meta"], d["score"], d["has_svg"]))
            else:
                lines.append("    <td></td>")
        lines.append("  </tr>")
    lines.append("</table>")

    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by [`generate_report.py`](../../generate_report.py)*")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DISPLAY_ORDER = [
    "01_temperature",
    "02_battery",
    "03_comfort_dual",
    "04_circular_gauge",
    "05_scrolling_graph",
    "06_dpad_menu",
    "07_compass",
    "09_watch",
    "08_smiley_happy",
    "08_smiley_sad",
    "08_smiley_surprised",
    "08_smiley_angry",
    "08_smiley_sleeping",
    "08_smiley_love",
    "08_smiley_reactive",
]


def main():
    discovered = find_tutorials()
    # Apply explicit display order; append any unlisted tutorials at the end
    ordered = [t for t in DISPLAY_ORDER if t in discovered]
    ordered += [t for t in discovered if t not in ordered]
    tutorials = ordered
    print(f"Found {len(tutorials)} tutorial(s).")

    data = {}
    for name in tutorials:
        print(f"\n[{name}]")
        meta = extract_metadata(name)
        print(f"  title: {meta.get('title', '?')}")

        print("  Running screenshot.py...")
        run_screenshot(name)

        has_svg = os.path.isfile(os.path.join(MOCKUPS_DIR, f"{name}.svg"))
        if has_svg:
            print("  Rasterizing SVG...")
            rasterize_svg(name)

        score = compute_ssim(name)
        if score is not None:
            status = "PASS" if score >= THRESHOLD_SSIM else "FAIL"
            print(f"  SSIM: {score:.4f} ({status})")
        else:
            print("  SSIM: n/a (no ref PNG or missing dependency)")

        data[name] = {"meta": meta, "score": score, "has_svg": has_svg}

    readme_path = os.path.join(MOCKUPS_DIR, "README.md")
    content = generate_report(tutorials, data)
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\nReport saved: {readme_path}")


if __name__ == "__main__":
    main()
