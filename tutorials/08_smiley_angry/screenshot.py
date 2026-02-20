"""
Screenshot generator for Tutorial 08 — Smiley (Angry).

Usage:
    python tutorials/08_smiley_angry/screenshot.py
"""

METADATA = {
    "title": "Smiley — Angry",
    "widget": "screen.face('angry')",
    "description": "Full-screen angry face expression",
}


def draw(screen):
    """Drawing code — runs on sim and board."""
    screen.clear()
    screen.face("angry")
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
    out_path = os.path.join(root, "docs", "mockups", "08_smiley_angry_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
