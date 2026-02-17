"""
Pillow-based simulator backend for steami_screen.

Mimics the SSD1327 display interface so that Screen works identically.
Renders to a grayscale PIL Image and can save to PNG with circular mask.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# MicroPython framebuf uses a built-in 8x8 pixel font.
# We approximate it with a small monospace truetype font.
_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
]


def _load_font(size=8):
    for path in _FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _color_to_gray(c):
    """Convert SSD1327 color (0-15) to 8-bit grayscale (0-255)."""
    return min(255, max(0, int(c) * 17))


class SimBackend:
    """Drop-in replacement for SSD1327 display, using Pillow."""

    def __init__(self, width=128, height=128, scale=1):
        self.width = width
        self.height = height
        self.scale = scale  # render at higher res for nicer output
        sw = width * scale
        sh = height * scale
        self._img = Image.new("L", (sw, sh), 0)
        self._draw = ImageDraw.Draw(self._img)
        # MicroPython framebuf: 8x8 bitmap, square glyphs.
        # TrueType monospace: taller than wide, thicker strokes.
        # Use ~60% of nominal size to visually match the framebuf weight.
        base = int(8 * scale)
        self._font = _load_font(base)
        # Value text needs to be proportionally bigger to match
        # SVG mockups (value ~18% of screen vs title ~6%)
        self._font_medium = _load_font(int(base * 1.3))
        self._font_large = {
            2: _load_font(int(base * 2.8)),
            3: _load_font(int(base * 4)),
        }

    def fill(self, color):
        c = _color_to_gray(color)
        self._draw.rectangle(
            [0, 0, self._img.width - 1, self._img.height - 1], fill=c
        )

    def pixel(self, x, y, color):
        s = self.scale
        c = _color_to_gray(color)
        if s == 1:
            self._draw.point((x, y), fill=c)
        else:
            self._draw.rectangle([x * s, y * s, (x + 1) * s - 1, (y + 1) * s - 1], fill=c)

    def _centered_x(self, string, x, font, char_w):
        """Adjust x so text is centered around where the 8px-grid expects it."""
        s = self.scale
        expected_w = len(string) * char_w * s
        actual_w = font.getlength(string)
        return x * s + (expected_w - actual_w) / 2

    def text(self, string, x, y, color):
        s = self.scale
        c = _color_to_gray(color)
        ax = self._centered_x(string, x, self._font, 8)
        self._draw.text((ax, y * s), string, fill=c, font=self._font)

    def draw_medium_text(self, string, x, y, color):
        """Draw text slightly larger than base (for units, labels)."""
        s = self.scale
        c = _color_to_gray(color)
        ax = self._centered_x(string, x, self._font_medium, 8)
        self._draw.text((ax, y * s), string, fill=c,
                        font=self._font_medium)

    def draw_scaled_text(self, string, x, y, color, text_scale):
        """Draw text at a larger scale using a bigger font."""
        s = self.scale
        c = _color_to_gray(color)
        font = self._font_large.get(text_scale, self._font)
        ax = self._centered_x(string, x, font, 8 * text_scale)
        self._draw.text((ax, y * s), string, fill=c, font=font)

    def line(self, x1, y1, x2, y2, color):
        s = self.scale
        c = _color_to_gray(color)
        self._draw.line(
            [(x1 * s, y1 * s), (x2 * s, y2 * s)], fill=c, width=s
        )

    def fill_rect(self, x, y, w, h, color):
        s = self.scale
        c = _color_to_gray(color)
        self._draw.rectangle(
            [x * s, y * s, (x + w) * s - 1, (y + h) * s - 1], fill=c
        )

    def rect(self, x, y, w, h, color):
        s = self.scale
        c = _color_to_gray(color)
        self._draw.rectangle(
            [x * s, y * s, (x + w) * s - 1, (y + h) * s - 1], outline=c
        )

    def show(self):
        """No-op for simulator."""
        pass

    def save(self, path, circular=True, border=True):
        """Save the rendered image to a PNG file.

        Args:
            path: output PNG file path.
            circular: apply circular mask to simulate round screen.
            border: draw a border ring around the screen.
        """
        w, h = self._img.size
        result = self._img.copy()

        if circular:
            # Circular mask
            mask = Image.new("L", (w, h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([0, 0, w - 1, h - 1], fill=255)

            # Apply mask: black outside the circle
            bg = Image.new("L", (w, h), 0)
            result = Image.composite(result, bg, mask)

            if border:
                draw = ImageDraw.Draw(result)
                border_color = _color_to_gray(5)
                s = self.scale
                draw.ellipse(
                    [s, s, w - s - 1, h - s - 1],
                    outline=border_color, width=max(1, 2 * s)
                )

        result.save(path)
        return result
