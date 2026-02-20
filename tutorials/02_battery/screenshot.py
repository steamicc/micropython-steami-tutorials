"""
Screenshot generator for Tutorial 02 — Battery.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/02_battery/screenshot.py
"""

METADATA = {
    "title": "Battery",
    "widget": "screen.bar(soc)",
    "description": "Battery state of charge from BQ27441 gauge",
}


def draw(screen):
    """Drawing code — runs on sim and board."""
    pct = 72
    mv = 3842
    screen.clear()
    screen.title("Battery")
    screen.value("{}%".format(pct), y_offset=-15)
    screen.bar(pct, y_offset=-12, color=GREEN)
    screen.subtitle("{} mV".format(mv), "BQ27441")
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
    out_path = os.path.join(root, "docs", "mockups", "02_battery_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
