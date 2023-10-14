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
import adafruit_ntp
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

ntp = adafruit_ntp.NTP(
    pool,
    tz_offset=os.getenv("TZ_OFFSET", 0),
    socket_timeout=60,
)

aio_username = os.getenv("AIO_USER")
aio_key = os.getenv("AIO_KEY")

text_feed = f"{aio_username}/feeds/paging.text"


def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print(
        f"Connected to Adafruit IO! Listening for topic changes on {text_feed}")
    client.subscribe(text_feed, qos=1)
    # Only because we're not using persistent messages.
    magtag.set_text("", 1)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Adafruit IO!")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print(f"New message on topic {topic}: {message}")
    magtag.set_text(message, 1)


ssl_context = ssl.create_default_context()
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=aio_username,
    password=aio_key,
    socket_pool=pool,
    ssl_context=ssl_context,
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

magtag.set_text("NTP...", 1)
print("Grabbing time")
while True:
    try:
        rtc.RTC().datetime = ntp.datetime
    except Exception:
        continue
    else:
        break


print("Connecting to MQTT")
mqtt_client.connect()


def sync_ntp():
    print("Resyncing Time")
    try:
        rtc.RTC().datetime = ntp.datetime
    except Exception as exc:
        print("Error pulling NTP:", exc)


schedule.every(15).minutes.do(sync_ntp)


refresh_display()

print("Starting loop")
while True:
    mqtt_client.loop()
    schedule.run_pending()
    time.sleep(1)
