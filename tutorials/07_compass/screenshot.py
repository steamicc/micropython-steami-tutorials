"""
Screenshot generator for Tutorial 07 — Compass.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/07_compass/screenshot.py
"""

import sys
import os

# Add project paths
root = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(root, "lib"))
sys.path.insert(0, os.path.join(root, "sim"))

from steami_screen import Screen
from sim_backend import SimBackend

# --- Simulated display (scale 3x for readable PNG) ---
backend = SimBackend(128, 128, scale=3)
screen = Screen(backend)

# --- Same drawing code as main.py, with fixed values ---
heading = 0  # Pointing North, matching the SVG mockup

screen.clear()
screen.compass(heading)
screen.show()

# --- Save PNG ---
out_dir = os.path.join(root, "docs", "mockups")
out_path = os.path.join(out_dir, "07_compass_sim.png")
backend.save(out_path)
print("Saved:", out_path)
