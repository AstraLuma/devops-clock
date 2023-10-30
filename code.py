#!/usr/bin/python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: FAFOL

import os

import rtc
import socketpool
import ssl
import time
import wifi

from adafruit_magtag.magtag import MagTag
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_requests
import augmented_ntp
import circuitpython_schedule as schedule

magtag = MagTag()
magtag.add_text(
    text_position=(
        (magtag.graphics.display.width // 2),
        (magtag.graphics.display.height // 3),
    ),
    text_scale=3,
    text_anchor_point=(0.5, 0.5),
)

magtag.add_text(
    text_position=(
        (magtag.graphics.display.width // 2),
        (magtag.graphics.display.height * 2 // 3),
    ),
    text_scale=2,
    text_anchor_point=(0.5, 0.5),
)


old_time = (0, 0)


def refresh_display():
    global old_time
    now = time.localtime()
    if (now.tm_hour, now.tm_min) != old_time:
        print("Updating display")
        magtag.set_text(f"{now.tm_hour:02}:{now.tm_min:02}", 0)
        old_time = (now.tm_hour, now.tm_min)


schedule.every(10).seconds.do(refresh_display)

refresh_display()

print("Doing WiFi")
magtag.set_text("WiFi...", 1)
wifi.radio.hostname = os.getenv('WIFI_HOSTNAME', 'magtag')
while True:
    try:
        wifi.radio.connect(
            os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD")
        )
    except ConnectionError:
        continue
    else:
        break

pool = socketpool.SocketPool(wifi.radio)
http = adafruit_requests.Session(pool)


ntp = augmented_ntp.NTP(
    pool,
    http,
    timezone=os.getenv('TIMEZONE', 'Etc/UTC'),
    tz_offset=0,
    socket_timeout=60,
)

magtag.set_text("NTP...", 1)
print("Grabbing time")
while True:
    try:
        rtc.RTC().datetime = ntp.localtime
    except Exception:
        continue
    else:
        break


def sync_ntp():
    print("Resyncing Time")
    try:
        rtc.RTC().datetime = ntp.datetime
    except Exception as exc:
        print("Error pulling NTP:", exc)


schedule.every(15).minutes.do(sync_ntp)


magtag.set_text('', 1)

refresh_display()

print("Starting loop")
while True:
    schedule.run_pending()
    time.sleep(1)
