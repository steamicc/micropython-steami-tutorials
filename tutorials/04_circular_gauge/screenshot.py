"""
Screenshot generator for Tutorial 04 — Circular Gauge.

Uses the Pillow simulator backend to produce a PNG that matches
what the real screen would display, for documentation and validation.

Usage:
    python tutorials/04_circular_gauge/screenshot.py
"""

METADATA = {
    "title": "Circular Gauge",
    "widget": "screen.gauge(dist, min_val, max_val, unit)",
    "description": "Distance visualized as a circular arc gauge (VL53L1X ToF)",
}


def draw(screen):
    """Drawing code — runs on sim and board."""
    dist = 342
    screen.clear()
    screen.gauge(dist, min_val=0, max_val=500, unit="mm")
    screen.title("Distance")
    screen.subtitle("VL53L1X ToF")
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
    out_path = os.path.join(root, "docs", "mockups", "04_circular_gauge_sim.png")
    backend.save(out_path)
    print("Saved:", out_path)
