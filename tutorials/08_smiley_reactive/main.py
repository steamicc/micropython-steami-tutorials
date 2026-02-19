"""
Tutorial 08 — Reactive Smiley
Displays pixel-art face expressions that react to distance sensor input.
"""

from machine import SPI, Pin, I2C
import ssd1327
import time

# --- Screen setup ---
spi = SPI(1)
dc = Pin("DATA_COMMAND_DISPLAY")
res = Pin("RST_DISPLAY")
cs = Pin("CS_DISPLAY")
from steami_ssd1327 import SSD1327Display
display = SSD1327Display(ssd1327.WS_OLED_128X128_SPI(spi, dc, res, cs))

# --- High-level screen API ---
import sys
sys.path.append("/lib")
from steami_screen import Screen, GREEN, RED, YELLOW, LIGHT

screen = Screen(display)

# --- Sensor setup ---
i2c = I2C(1)
from vl53l1x import VL53L1X
sensor = VL53L1X(i2c)


def choose_expression(dist):
    """Pick a face based on distance (mm)."""
    if dist < 50:
        return "surprised", "SURPRISED", YELLOW
    elif dist < 150:
        return "happy", "HAPPY", GREEN
    elif dist < 300:
        return "sleeping", "SLEEPING", LIGHT
    else:
        return "sad", "SAD", RED


# --- Main loop ---
while True:
    dist = sensor.read()
    expr, label, color = choose_expression(dist)

    screen.clear()
    screen.title("Mood")
    screen.face(expr, color=color)
    screen.subtitle(label, "dist:{}mm".format(dist))
    screen.show()

    time.sleep(0.2)
