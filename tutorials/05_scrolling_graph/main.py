"""
Tutorial 05 — Scrolling Graph
Displays APDS9960 ambient light with a scrolling line graph.
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
from apds9960 import APDS9960
sensor = APDS9960(i2c)

# --- Data buffer (scrolling window) ---
MAX_POINTS = 20
data = []

# --- Main loop ---
while True:
    lux = sensor.read_light()
    data.append(lux)
    if len(data) > MAX_POINTS:
        data.pop(0)

    screen.clear()
    screen.title("Light (lux)")
    screen.graph(data, min_val=0, max_val=1000)
    screen.subtitle("APDS9960", "20s window")
    screen.show()

    time.sleep(1)
