"""
Tutorial 09 — Analog Watch
Displays an analog clock face using the built-in RTC.
"""

from machine import SPI, Pin, RTC
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

# --- RTC setup ---
rtc = RTC()

# --- Main loop ---
while True:
    _, _, _, _, h, m, s, _ = rtc.datetime()

    screen.clear()
    screen.watch(h, m, s)
    screen.show()

    time.sleep(0.5)
