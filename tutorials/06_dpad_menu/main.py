"""
Tutorial 06 — D-pad Menu
Displays a scrollable menu navigated with the D-pad buttons.
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

# --- D-pad setup ---
i2c = I2C(1)
from mcp23009e import MCP23009E
from mcp23009e.const import *

reset = Pin("RST_EXPANDER", Pin.OUT)
mcp = MCP23009E(i2c, address=MCP23009_I2C_ADDR, reset_pin=reset)

mcp.setup(MCP23009_BTN_UP, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)
mcp.setup(MCP23009_BTN_DOWN, MCP23009_DIR_INPUT, pullup=MCP23009_PULLUP)

# --- Menu items ---
items = ["Temperature", "Humidity", "Distance", "Light", "Battery", "Proximity"]
selected = 0

# --- Main loop ---
while True:
    if mcp.get_level(MCP23009_BTN_UP) == MCP23009_LOGIC_LOW:
        selected = (selected - 1) % len(items)
        time.sleep(0.2)

    if mcp.get_level(MCP23009_BTN_DOWN) == MCP23009_LOGIC_LOW:
        selected = (selected + 1) % len(items)
        time.sleep(0.2)

    screen.clear()
    screen.title("Menu")
    screen.menu(items, selected=selected)
    screen.show()

    time.sleep(0.05)
