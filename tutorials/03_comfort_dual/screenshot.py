"""
Screenshot generator for Tutorial 03 — Comfort (dual display).

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/03_comfort_dual/screenshot.py
"""

METADATA = {
    "title": "Comfort (dual)",
    "widget": "screen.value() x2",
    "description": "Temperature and humidity side by side (HTS221)",
}


def draw(screen):
    """Drawing code — runs on sim and board."""
    temp = 23.5
    hum = 45
    screen.clear()
    screen.title("Comfort")
    screen.line(64, 32, 64, 96, color=DARK)
    screen.value(temp, unit="°C", at="W", label="TEMP")
    screen.value(int(hum), unit="%", at="E", label="HUM")
    screen.subtitle("Comfortable", "HTS221", color=GREEN)
    screen.show()


# --- PC runner ---
if __name__ == "__main__":
    import sys
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    sys.path.insert(0, os.path.join(root, "lib"))
    sys.path.insert(0, os.path.join(root, "sim"))
    from steami_screen import Screen, GREEN, DARK  # noqa: E402
    from sim_backend import SimBackend  # noqa: E402
    backend = SimBackend(128, 128, scale=3)
    draw(Screen(backend))
    out_path = os.path.join(root, "docs", "mockups", "03_comfort_dual_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
