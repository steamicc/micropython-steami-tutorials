"""
Screenshot generator for Tutorial 08 — Smiley (Happy).

Usage:
    python tutorials/08_smiley_happy/screenshot.py
"""

METADATA = {
    "title": "Smiley — Happy",
    "widget": "screen.face('happy')",
    "description": "Full-screen happy face expression",
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

# --- Immersive face ---
screen.clear()
screen.face("happy")
screen.show()

# --- Save PNG ---
out_dir = os.path.join(root, "docs", "mockups")
out_path = os.path.join(out_dir, "08_smiley_happy_sim.png")
backend.save(out_path)
print("Saved:", out_path)
