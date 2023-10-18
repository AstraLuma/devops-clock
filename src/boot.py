import os
import wifi

wifi.radio.hostname = os.getenv('CIRCUITPY_WIFI_HOSTNAME', wifi.radio.hostname)