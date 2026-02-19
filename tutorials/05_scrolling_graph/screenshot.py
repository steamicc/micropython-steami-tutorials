"""
Screenshot generator for Tutorial 05 — Scrolling Graph.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/05_scrolling_graph/screenshot.py
"""

METADATA = {
    "title": "Scrolling Graph",
    "widget": "screen.graph(data, min_val, max_val)",
    "description": "Light level history as a scrolling line graph (APDS9960)",
}

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
# Simulated light data (rising trend, matching SVG mockup)
data = [350, 375, 410, 390, 450, 525, 560, 540, 575, 610,
        590, 625, 600, 640, 610, 625, 590, 610, 650, 847]

screen.clear()
screen.title("Light (lux)")
screen.graph(data, min_val=0, max_val=1000)
screen.subtitle("APDS9960", "20s window")
screen.show()

# --- Save PNG ---
out_dir = os.path.join(root, "docs", "mockups")
out_path = os.path.join(out_dir, "05_scrolling_graph_sim.png")
backend.save(out_path)
print("Saved:", out_path)
