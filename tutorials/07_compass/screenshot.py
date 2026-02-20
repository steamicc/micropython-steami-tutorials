"""
Screenshot generator for Tutorial 07 — Compass.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/07_compass/screenshot.py
"""

METADATA = {
    "title": "Compass",
    "widget": "screen.compass(heading)",
    "description": "Compass rose with heading needle and cardinal labels",
}


def draw(screen):
    """Drawing code — runs on sim and board."""
    heading = 0
    screen.clear()
    screen.compass(heading)
    screen.show()


# --- PC runner ---
if __name__ == "__main__":
    import sys
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    sys.path.insert(0, os.path.join(root, "lib"))
    sys.path.insert(0, os.path.join(root, "sim"))
    from steami_screen import Screen  # noqa: E402
    from sim_backend import SimBackend  # noqa: E402
    backend = SimBackend(128, 128, scale=3)
    draw(Screen(backend))
    out_path = os.path.join(root, "docs", "mockups", "07_compass_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
