"""
Screenshot generator for Tutorial 09 — Analog Watch.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/09_watch/screenshot.py
"""

METADATA = {
    "title": "Analog Watch",
    "widget": "screen.watch(hours, minutes, seconds)",
    "description": "Classical analog watch face with hour, minute and second hands",
}


def draw(screen):
    """Drawing code — runs on sim and board."""
    screen.clear()
    screen.watch(10, 10, 30)
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
    out_path = os.path.join(root, "docs", "mockups", "09_watch_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
