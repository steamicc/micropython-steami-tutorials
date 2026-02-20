"""
Screenshot generator for Tutorial 01 — Temperature.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/01_temperature/screenshot.py
"""

METADATA = {
    "title": "Temperature",
    "widget": "screen.value(temp, unit='C')",
    "description": "Reads temperature from HTS221 sensor",
}


def draw(screen):
    """Drawing code — runs on sim and board."""
    temp = 23.5
    screen.clear()
    screen.title("Temperature")
    screen.value(temp, unit="°C")
    screen.subtitle("HTS221 sensor")
    screen.show()


# --- PC runner ---
if __name__ == "__main__":
    import sys
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, os.path.join(root, "lib"))
    sys.path.insert(0, os.path.join(root, "sim"))
    from steami_screen import Screen
    from sim_backend import SimBackend
    backend = SimBackend(128, 128, scale=3)
    draw(Screen(backend))
    out_path = os.path.join(root, "docs", "mockups", "01_temperature_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
