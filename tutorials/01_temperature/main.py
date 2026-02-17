"""
Tutorial 01 — Temperature
Displays the HTS221 temperature reading on the round screen.
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
from steami_screen import Screen, WHITE, GRAY, LIGHT, DARK

screen = Screen(display)

# --- Sensor setup ---
i2c = I2C(1)
sensor = HTS221(i2c)

# --- Main loop ---
while True:
    temp = sensor.temperature()

    screen.clear()
    screen.title("Temperature")
    screen.value(round(temp, 1), unit="C")
    screen.subtitle("HTS221 sensor")
    screen.show()

    print("Temperature: {:.1f} C".format(temp))
    time.sleep(0.5)
