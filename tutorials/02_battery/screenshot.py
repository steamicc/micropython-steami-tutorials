"""
Screenshot generator for Tutorial 02 — Battery.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/02_battery/screenshot.py
"""

import sys
import os

# Add project paths
root = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(root, "lib"))
sys.path.insert(0, os.path.join(root, "sim"))

from steami_screen import Screen, DARK, GREEN
from sim_backend import SimBackend

# --- Simulated display (scale 3x for readable PNG) ---
backend = SimBackend(128, 128, scale=3)
screen = Screen(backend)

# --- Same drawing code as main.py, with fixed values ---
pct = 72
mv = 3842

screen.clear()
screen.title("Battery")
screen.value("{}%".format(pct), y_offset=-15)
screen.bar(pct, y_offset=-12, color=GREEN)
# Two subtitle lines (Level 3 pixel API for precise placement)
cx = screen.width // 2
line1 = "{} mV".format(mv)
line2 = "BQ27441"
backend.draw_small_text(line1, cx - len(line1) * 4, 94, DARK)
backend.draw_small_text(line2, cx - len(line2) * 4, 105, DARK)
screen.show()

# --- Save PNG ---
out_dir = os.path.join(root, "docs", "mockups")
out_path = os.path.join(out_dir, "02_battery_sim.png")
backend.save(out_path)
print("Saved:", out_path)
