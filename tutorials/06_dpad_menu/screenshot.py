"""
Screenshot generator for Tutorial 06 — D-pad Menu.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/06_dpad_menu/screenshot.py
"""

METADATA = {
    "title": "D-pad Menu",
    "widget": "screen.menu(items, selected)",
    "description": "Scrollable menu navigated with D-pad buttons (MCP23009E)",
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
items = ["Temperature", "Humidity", "Distance", "Light", "Battery", "Proximity"]
selected = 2  # "Distance" selected, matching SVG mockup

screen.clear()
screen.title("Menu")
screen.menu(items, selected=selected)
screen.show()

# --- Save PNG ---
out_dir = os.path.join(root, "docs", "mockups")
out_path = os.path.join(out_dir, "06_dpad_menu_sim.png")
backend.save(out_path)
print("Saved:", out_path)
