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


def draw(screen):
    """Drawing code — runs on sim and board."""
    data = [350, 375, 410, 390, 450, 525, 560, 540, 575, 610, 590, 625, 600, 640, 610, 625, 590, 610, 650, 847]
    screen.clear()
    screen.title("Light (lux)")
    screen.graph(data, min_val=0, max_val=1000)
    screen.subtitle("APDS9960", "20s window")
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
    out_path = os.path.join(root, "docs", "mockups", "05_scrolling_graph_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
