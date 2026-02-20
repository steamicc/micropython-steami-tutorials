"""
Screenshot generator for Tutorial 08 — Reactive Smiley.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/08_smiley_reactive/screenshot.py
"""

METADATA = {
    "title": "Smiley — Reactive",
    "widget": "screen.face(mood)",
    "description": "Compact face with title and mood label, reactive to sensor input",
}


def draw(screen):
    """Drawing code — runs on sim and board."""
    screen.clear()
    screen.title("Mood")
    screen.face("happy")
    screen.subtitle("HAPPY", color=GREEN)
    screen.show()


# --- PC runner ---
if __name__ == "__main__":
    import sys
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    sys.path.insert(0, os.path.join(root, "lib"))
    sys.path.insert(0, os.path.join(root, "sim"))
    from steami_screen import Screen, GREEN  # noqa: E402
    from sim_backend import SimBackend  # noqa: E402
    backend = SimBackend(128, 128, scale=3)
    draw(Screen(backend))
    out_path = os.path.join(root, "docs", "mockups", "08_smiley_reactive_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
