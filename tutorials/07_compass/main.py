"""
Tutorial 07 — Compass
Displays a compass with a rotating needle based on the LSM6DSL gyroscope.
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
from lsm6dsl import LSM6DSL
sensor = LSM6DSL(i2c)

heading = 0

# --- Main loop ---
while True:
    gz = sensor.gyro()[2]
    heading = (heading + gz * 0.1) % 360

    screen.clear()
    screen.compass(heading)
    screen.show()

    time.sleep(0.05)
