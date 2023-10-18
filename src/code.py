import time
import os

import board
import rtc
import socketpool
import wifi

import adafruit_ntp

import tm1640


LOADING = 0x00_00_80_00_00_00_00_00_00_00_00_00_00_00_00_00

print("Setup")
tm = tm1640.TM1640(board.SCK, board.MOSI)

tm.display_on(7)

print("NTP...")
tm.set_data_int(0, LOADING)

pool = socketpool.SocketPool(wifi.radio)

ntp = adafruit_ntp.NTP(
    pool,
    tz_offset=os.getenv("TZ_OFFSET", 0),
    socket_timeout=60,
)

while True:
    try:
        rtc.RTC().datetime = ntp.datetime
    except Exception:
        continue
    else:
        break

frame = 1
while True:
    print(time.localtime())

    tm.set_data_int(0, frame)
    frame <<= 1
    if not frame & tm1640.FRAME_MASK:
        frame = 0

    time.sleep(60)
