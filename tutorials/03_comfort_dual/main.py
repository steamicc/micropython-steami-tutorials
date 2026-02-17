"""
Tutorial 03 — Comfort (dual display)
Shows temperature and humidity side by side with a comfort indicator.
"""

from machine import SPI, Pin, I2C
from hts221 import HTS221
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
from steami_screen import Screen, GREEN, DARK

screen = Screen(display)

# --- Sensor setup ---
i2c = I2C(1)
sensor = HTS221(i2c)


def comfort_label(temp, hum):
    """Simple comfort index based on temperature and humidity."""
    if 20 <= temp <= 26 and 30 <= hum <= 60:
        return "Comfortable"
    elif temp < 18 or hum < 20:
        return "Too dry/cold"
    else:
        return "Uncomfortable"


# --- Main loop ---
while True:
    temp = round(sensor.temperature(), 1)
    hum = round(sensor.humidity(), 0)
    label = comfort_label(temp, hum)

    screen.clear()
    screen.title("Comfort")
    screen.line(64, 32, 64, 96, color=DARK)
    screen.value(temp, unit="°C", at="W", label="TEMP")
    screen.value(int(hum), unit="%", at="E", label="HUM")
    screen.subtitle(label, "HTS221", color=GREEN)
    screen.show()

    time.sleep(1)
