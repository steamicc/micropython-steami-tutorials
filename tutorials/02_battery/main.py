"""
Tutorial 02 — Battery
Displays the BQ27441 battery level with a progress bar.
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
from steami_screen import Screen, GREEN

screen = Screen(display)

# --- Sensor setup ---
i2c = I2C(1)
# BQ27441 battery fuel gauge at default I2C address
from bq27441 import BQ27441
gauge = BQ27441(i2c)

# --- Main loop ---
while True:
    pct = gauge.state_of_charge()
    mv = gauge.voltage()

    screen.clear()
    screen.title("Battery")
    screen.value("{}%".format(pct), y_offset=-15)
    screen.bar(pct, y_offset=-12, color=GREEN)
    screen.subtitle("{} mV".format(mv), "BQ27441")
    screen.show()

    time.sleep(1)
