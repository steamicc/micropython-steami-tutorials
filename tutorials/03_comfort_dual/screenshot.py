"""
Screenshot generator for Tutorial 03 — Comfort (dual display).

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/03_comfort_dual/screenshot.py
"""

import sys
import os

# Add project paths
root = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(root, "lib"))
sys.path.insert(0, os.path.join(root, "sim"))

from steami_screen import Screen, GREEN, DARK
from sim_backend import SimBackend

# --- Simulated display (scale 3x for readable PNG) ---
backend = SimBackend(128, 128, scale=3)
screen = Screen(backend)

# --- Same drawing code as main.py, with fixed values ---
temp = 23.5
hum = 45

screen.clear()
screen.title("Comfort")
screen.line(64, 32, 64, 96, color=DARK)
screen.value(temp, unit="°C", at="W", label="TEMP")
screen.value(int(hum), unit="%", at="E", label="HUM")
screen.subtitle("Comfortable", "HTS221", color=GREEN)
screen.show()

# --- Save PNG ---
out_dir = os.path.join(root, "docs", "mockups")
out_path = os.path.join(out_dir, "03_comfort_dual_sim.png")
backend.save(out_path)
print("Saved:", out_path)
