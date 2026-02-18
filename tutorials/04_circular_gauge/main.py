"""
Tutorial 04 — Circular Gauge
Displays VL53L1X time-of-flight distance with an arc gauge.
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
from steami_screen import Screen

screen = Screen(display)

# --- Sensor setup ---
i2c = I2C(1)
from vl53l1x import VL53L1X
sensor = VL53L1X(i2c)

# --- Main loop ---
while True:
    dist = sensor.read()

    screen.clear()
    screen.gauge(dist, min_val=0, max_val=500, unit="mm")
    screen.title("Distance")
    screen.subtitle("VL53L1X ToF")
    screen.show()

    time.sleep(0.2)
