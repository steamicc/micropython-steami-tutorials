"""
steami_screen — High-level API for the STeaMi round display.

Works with any backend that implements the display interface:
  - SSD1327 (128x128 grayscale OLED)
  - GC9A01  (240x240 RGB TFT)
  - SimBackend (Pillow, for screenshots and validation)

3-level API:
  Level 1 — Widgets:  title(), value(), subtitle(), bar(), gauge(), compass()...
  Level 2 — Cardinal: text("hello", at="NE"), line(...), circle(...)
  Level 3 — Pixels:   pixel(x, y, color) with screen.center, screen.radius
"""

import math

# --- Color constants (SSD1327 grayscale 0-15) ---

BLACK = 0
DARK = 6
GRAY = 9
LIGHT = 11
WHITE = 15

# --- Cardinal position names ---

_CARDINALS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW", "CENTER")


class Screen:
    """High-level wrapper around a raw display backend."""

    CHAR_W = 8   # framebuf built-in font width
    CHAR_H = 8   # framebuf built-in font height

    def __init__(self, display, width=128, height=128):
        self._d = display
        self.width = width
        self.height = height

    # --- Adaptive properties ---

    @property
    def center(self):
        return (self.width // 2, self.height // 2)

    @property
    def radius(self):
        return min(self.width, self.height) // 2

    @property
    def max_chars(self):
        return self.width // self.CHAR_W

    # --- Cardinal position resolver ---

    def _safe_margin(self, tw, from_edge):
        """Compute the minimum Y margin from top/bottom so that text of
        width `tw` fits inside the circle. `from_edge` is the baseline
        distance from the circle edge."""
        r = self.radius
        # At distance d from center, available width = 2*sqrt(r^2 - d^2)
        # We need 2*sqrt(r^2 - d^2) >= tw, so d <= sqrt(r^2 - (tw/2)^2)
        half_tw = tw / 2
        if half_tw >= r:
            return r  # text too wide, push to center
        max_d = math.sqrt(r * r - half_tw * half_tw)
        # margin from top = cy - max_d = r - max_d
        min_margin = r - int(max_d)
        return max(min_margin + 2, from_edge)  # +2px padding

    def _resolve(self, at, text_len=0, scale=1):
        """Return (x, y) for a cardinal position, centering text if needed."""
        cx, cy = self.center
        r = self.radius
        ch = self.CHAR_H * scale
        tw = text_len * self.CHAR_W * scale  # total text pixel width

        # Margins adapted to circular screen
        margin_ns = self._safe_margin(tw, ch)     # N/S: depends on text width
        margin_ew = ch + 4                         # E/W: fixed side margin

        positions = {
            "N":      (cx - tw // 2, margin_ns),
            "NE":     (self.width - margin_ew - tw, margin_ns),
            "E":      (self.width - margin_ew - tw, cy - ch // 2),
            "SE":     (self.width - margin_ew - tw, self.height - margin_ns - ch),
            "S":      (cx - tw // 2, self.height - margin_ns - ch),
            "SW":     (margin_ew, self.height - margin_ns - ch),
            "W":      (margin_ew, cy - ch // 2),
            "NW":     (margin_ew, margin_ns),
            "CENTER": (cx - tw // 2, cy - ch // 2),
        }
        return positions.get(at, positions["CENTER"])

    # --- Level 1: Widgets ---

    def title(self, text, color=GRAY):
        """Draw title text at the top (N)."""
        x, y = self._resolve("N", len(text))
        self._d.text(text, x, y, color)

    def value(self, val, unit=None, at="CENTER", label=None, color=WHITE, scale=2):
        """Draw a large value, optionally with unit below and label above."""
        text = str(val)
        cx, cy = self.center
        char_w = self.CHAR_W * scale
        char_h = self.CHAR_H * scale
        tw = len(text) * char_w

        if at == "CENTER":
            x = cx - tw // 2
            if unit:
                # Center the full block (value + gap + unit) vertically
                gap = char_h // 2
                unit_h = self.CHAR_H
                block_h = char_h + gap + unit_h
                y = cy - block_h // 2  # visual center biased up
            else:
                y = cy - char_h // 2
        elif at == "W":
            x = self.width // 4 - tw // 2
            y = cy - char_h // 2
        elif at == "E":
            x = 3 * self.width // 4 - tw // 2
            y = cy - char_h // 2
        else:
            x, y = self._resolve(at, len(text), scale)

        # Optional label above
        if label:
            lx = x + tw // 2 - len(label) * self.CHAR_W // 2
            self._d.text(label, lx, y - self.CHAR_H - 4, GRAY)

        # Value (large)
        self._draw_scaled_text(text, x, y, color, scale)

        # Optional unit below (medium font if backend supports it)
        if unit:
            unit_y = y + char_h + char_h // 2
            ux = x + tw // 2 - len(unit) * self.CHAR_W // 2
            if hasattr(self._d, 'draw_medium_text'):
                self._d.draw_medium_text(unit, ux, unit_y, LIGHT)
            else:
                self._d.text(unit, ux, unit_y, LIGHT)

    def subtitle(self, text, color=DARK):
        """Draw subtitle text at the bottom (S)."""
        x, y = self._resolve("S", len(text))
        self._d.text(text, x, y + self.CHAR_H, color)

    def bar(self, val, max_val=100, y_offset=0, color=LIGHT):
        """Draw a horizontal progress bar below center."""
        cx, cy = self.center
        bar_w = self.width - 40
        bar_h = 8
        bx = cx - bar_w // 2
        by = cy + 20 + y_offset
        fill_w = int(bar_w * min(val, max_val) / max_val)

        # Background
        self._fill_rect(bx, by, bar_w, bar_h, DARK)
        # Fill
        if fill_w > 0:
            self._fill_rect(bx, by, fill_w, bar_h, color)

    def gauge(self, val, min_val=0, max_val=100, unit=None, color=LIGHT):
        """Draw a circular arc gauge (270 deg, gap at bottom)."""
        cx, cy = self.center
        r = self.radius - 8
        start_angle = 135
        sweep = 270
        ratio = (val - min_val) / (max_val - min_val)
        ratio = max(0.0, min(1.0, ratio))

        # Background arc
        self._draw_arc(cx, cy, r, start_angle, sweep, DARK)
        # Filled arc
        if ratio > 0:
            self._draw_arc(cx, cy, r, start_angle, int(sweep * ratio), color)

        # Value in center
        text = str(val)
        self._draw_scaled_text(
            text,
            cx - len(text) * self.CHAR_W,
            cy - self.CHAR_H,
            WHITE, 2
        )
        # Unit below value
        if unit:
            self._d.text(
                unit,
                cx - len(unit) * self.CHAR_W // 2,
                cy + self.CHAR_H + 2,
                LIGHT
            )

    def graph(self, data, min_val=0, max_val=100, color=LIGHT):
        """Draw a scrolling line graph in the lower portion."""
        cx, cy = self.center
        margin = 20
        gx = margin + 10
        gy = cy - 5
        gw = self.width - margin * 2 - 10
        gh = self.height - gy - margin

        # Y axis
        self._vline(gx, gy, gh, DARK)
        # X axis
        self._hline(gx, gy + gh, gw, DARK)

        if len(data) < 2:
            return

        # Map data points to graph area
        step = gw / (len(data) - 1) if len(data) > 1 else gw
        span = max_val - min_val
        if span == 0:
            span = 1

        prev_px, prev_py = None, None
        for i, v in enumerate(data):
            px = int(gx + i * step)
            ratio = (v - min_val) / span
            ratio = max(0.0, min(1.0, ratio))
            py = int(gy + gh - ratio * gh)
            if prev_px is not None:
                self._line(prev_px, prev_py, px, py, color)
            prev_px, prev_py = px, py

    def menu(self, items, selected=0, color=WHITE):
        """Draw a scrollable list menu."""
        cx, cy = self.center
        item_h = self.CHAR_H + 6
        visible = min(len(items), (self.height - 40) // item_h)

        # Scroll window
        start = max(0, min(selected - visible // 2, len(items) - visible))
        y = 25

        for i in range(start, min(start + visible, len(items))):
            iy = y + (i - start) * item_h
            if i == selected:
                self._fill_rect(15, iy - 2, self.width - 30, item_h, DARK)
                self._d.text("> " + items[i], 18, iy, color)
            else:
                self._d.text("  " + items[i], 18, iy, GRAY)

    def compass(self, heading, color=LIGHT):
        """Draw a compass with a rotating needle."""
        cx, cy = self.center
        r = self.radius - 12

        # Rose circles
        self._draw_circle(cx, cy, r, DARK)
        self._draw_circle(cx, cy, int(r * 0.7), DARK)

        # Cardinal labels
        for label, angle in (("N", 0), ("E", 90), ("S", 180), ("W", 270)):
            lx = cx + int((r + 8) * math.sin(math.radians(angle)))
            ly = cy - int((r + 8) * math.cos(math.radians(angle)))
            c = WHITE if label == "N" else GRAY
            self._d.text(label, lx - self.CHAR_W // 2, ly - self.CHAR_H // 2, c)

        # Tick marks (8 directions)
        for angle in range(0, 360, 45):
            inner = r - 6
            outer = r
            rad = math.radians(angle)
            x1 = cx + int(inner * math.sin(rad))
            y1 = cy - int(inner * math.cos(rad))
            x2 = cx + int(outer * math.sin(rad))
            y2 = cy - int(outer * math.cos(rad))
            c = LIGHT if angle % 90 == 0 else DARK
            self._line(x1, y1, x2, y2, c)

        # Needle
        rad = math.radians(heading)
        needle_len = int(r * 0.85)
        half_w = 3

        # Tip (north side of needle, bright)
        nx = cx + int(needle_len * math.sin(rad))
        ny = cy - int(needle_len * math.cos(rad))
        # Tail (south side, dark)
        sx = cx - int(needle_len * math.sin(rad))
        sy = cy + int(needle_len * math.cos(rad))
        # Perpendicular offset for width
        px = int(half_w * math.cos(rad))
        py = int(half_w * math.sin(rad))

        # North half (bright)
        self._fill_triangle(nx, ny, cx - px, cy - py, cx + px, cy + py, color)
        # South half (dark)
        self._fill_triangle(sx, sy, cx - px, cy - py, cx + px, cy + py, DARK)

        # Center pivot
        self._fill_circle(cx, cy, 3, GRAY)

    # --- Level 2: Cardinal text & shapes ---

    def text(self, text, at="CENTER", color=WHITE, scale=1):
        """Draw text at a cardinal position or explicit (x,y)."""
        if isinstance(at, str):
            x, y = self._resolve(at, len(text), scale)
        else:
            x, y = at
        if scale > 1:
            self._draw_scaled_text(text, x, y, color, scale)
        else:
            self._d.text(text, x, y, color)

    def line(self, x1, y1, x2, y2, color=WHITE):
        self._line(x1, y1, x2, y2, color)

    def circle(self, x, y, r, color=WHITE, fill=False):
        if fill:
            self._fill_circle(x, y, r, color)
        else:
            self._draw_circle(x, y, r, color)

    def rect(self, x, y, w, h, color=WHITE, fill=False):
        if fill:
            self._fill_rect(x, y, w, h, color)
        else:
            self._rect(x, y, w, h, color)

    def pixel(self, x, y, color=WHITE):
        self._d.pixel(x, y, color)

    # --- Control ---

    def clear(self, color=BLACK):
        self._d.fill(color)

    def show(self):
        self._d.show()

    # --- Internal drawing helpers ---

    def _line(self, x1, y1, x2, y2, c):
        self._d.line(x1, y1, x2, y2, c)

    def _hline(self, x, y, w, c):
        self._d.line(x, y, x + w - 1, y, c)

    def _vline(self, x, y, h, c):
        self._d.line(x, y, x, y + h - 1, c)

    def _fill_rect(self, x, y, w, h, c):
        if hasattr(self._d, 'framebuf'):
            self._d.framebuf.fill_rect(x, y, w, h, c)
        elif hasattr(self._d, 'fill_rect'):
            self._d.fill_rect(x, y, w, h, c)
        else:
            for row in range(h):
                self._d.line(x, y + row, x + w - 1, y + row, c)

    def _rect(self, x, y, w, h, c):
        if hasattr(self._d, 'framebuf'):
            self._d.framebuf.rect(x, y, w, h, c)
        elif hasattr(self._d, 'rect'):
            self._d.rect(x, y, w, h, c)
        else:
            self._hline(x, y, w, c)
            self._hline(x, y + h - 1, w, c)
            self._vline(x, y, h, c)
            self._vline(x + w - 1, y, h, c)

    def _draw_scaled_text(self, text, x, y, color, scale):
        """Draw text at scale > 1 by scaling each pixel of the 8x8 font."""
        # Use framebuf built-in if available (MicroPython does not support scale)
        # Fallback: draw each char pixel-by-pixel at scale
        if hasattr(self._d, 'draw_scaled_text'):
            self._d.draw_scaled_text(text, x, y, color, scale)
            return
        # On real hardware without scaled text support, draw at scale=1
        # centered at the same position (best effort)
        if not hasattr(self._d, 'pixel'):
            self._d.text(text, x, y, color)
            return
        # Render at 1x to a temporary buffer, then scale up
        # For MicroPython: draw each character using the display's text method
        # but multiple times offset for a bold effect at scale 2
        if scale == 2:
            for dx in range(2):
                for dy in range(2):
                    self._d.text(text, x + dx, y + dy, color)
        elif scale == 3:
            for dx in range(3):
                for dy in range(3):
                    self._d.text(text, x + dx, y + dy, color)
        else:
            self._d.text(text, x, y, color)

    def _draw_arc(self, cx, cy, r, start_deg, sweep_deg, color):
        """Draw a thick arc (3px) using individual pixels."""
        steps = max(sweep_deg, 60)
        for i in range(steps + 1):
            angle = math.radians(start_deg + i * sweep_deg / steps)
            for dr in (-1, 0, 1):
                x = int(cx + (r + dr) * math.cos(angle))
                y = int(cy + (r + dr) * math.sin(angle))
                if 0 <= x < self.width and 0 <= y < self.height:
                    self._d.pixel(x, y, color)

    def _draw_circle(self, cx, cy, r, color):
        """Bresenham circle."""
        x, y, d = r, 0, 1 - r
        while x >= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                px, py = cx + sx, cy + sy
                if 0 <= px < self.width and 0 <= py < self.height:
                    self._d.pixel(px, py, color)
            y += 1
            if d < 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    def _fill_circle(self, cx, cy, r, color):
        """Filled circle using horizontal lines."""
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            y = cy + dy
            if 0 <= y < self.height:
                x1 = max(0, cx - dx)
                x2 = min(self.width - 1, cx + dx)
                self._d.line(x1, y, x2, y, color)

    def _fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle using scanline."""
        # Sort by y
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy_) = pts

        def interp(ya, xa, yb, xb, y):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) // (yb - ya)

        for y in range(ay, cy_ + 1):
            if y < by:
                xl = interp(ay, ax, cy_, cx, y)
                xr = interp(ay, ax, by, bx, y)
            else:
                xl = interp(ay, ax, cy_, cx, y)
                xr = interp(by, bx, cy_, cx, y)
            if xl > xr:
                xl, xr = xr, xl
            if 0 <= y < self.height:
                x_start = max(0, xl)
                x_end = min(self.width - 1, xr)
                if x_start <= x_end:
                    self._d.line(x_start, y, x_end, y, color)
