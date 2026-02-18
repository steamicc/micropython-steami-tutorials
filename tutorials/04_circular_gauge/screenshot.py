"""
Screenshot generator for Tutorial 04 — Circular Gauge.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/04_circular_gauge/screenshot.py
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
dist = 342

screen.clear()
screen.gauge(dist, min_val=0, max_val=500, unit="mm")
screen.title("Distance")
screen.subtitle("VL53L1X ToF")
screen.show()

# --- Save PNG ---
out_dir = os.path.join(root, "docs", "mockups")
out_path = os.path.join(out_dir, "04_circular_gauge_sim.png")
backend.save(out_path)
print("Saved:", out_path)
