import time

import busio
import digitalio
import board
from adafruit_bus_device.spi_device import SPIDevice

import tm1640

print("Setup")
tm = tm1640.TM1640(board.SCK, board.MOSI)

tm.display_on(7)

MASK = 0xFF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF_FF

print("All in")
tm.set_data_int(0, MASK)
time.sleep(5)

frame = 1

print("shimmer")
FRAME1 = 0x80_00_00_00_00_00_00_00_00_00_00_00_00_00_00_00
FRAME2 = 0x00_00_00_00_00_00_00_00_00_00_00_00_00_00_80_00
DELAY = 0.1

while False:
    tm.set_data_int(0, FRAME1)
    time.sleep(DELAY)
    tm.set_data_int(0, FRAME2)
    time.sleep(DELAY)

print("Individual")
while True:
    tm.set_data_int(0, frame)
    time.sleep(0.1)
    frame <<= 1
    if not frame & MASK:
        frame = 1
        print('.')
