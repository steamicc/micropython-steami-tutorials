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


def draw(screen):
    """Drawing code — runs on sim and board."""
    items = ["Temperature", "Humidity", "Distance", "Light", "Battery", "Proximity"]
    selected = 2
    screen.clear()
    screen.title("Menu")
    screen.menu(items, selected=selected)
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
    out_path = os.path.join(root, "docs", "mockups", "06_dpad_menu_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
