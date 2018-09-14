from drivers.logging import FileLogger

log = FileLogger.get_instance()
log.stdout = True

log.log("Boot start")

import sys
import machine
from time import sleep
import drivers.wifi as wifi

from weather_publisher import WeatherPublisher
from drivers.simple_ntp import SimpleNTP


# Disable wifi access point
wifi.access_point(disable=True)

# Connect to WIFI and wait for IP
wifi.connect()

failed_count = 0
while True:
    ip = wifi.get_ip()
    if ip is not None:
        log.log("Connected with IP: %s" % ip)
        break
    failed_count += 1
    log.log("Failed to connect to wifi %d times..." % failed_count)
    sleep(1)
    if failed_count > 60:
        machine.reset()

# Use the NTP to prime the local offset
ntp = SimpleNTP()
ntp.request_time()
log.log("Time synced from NTP, local: %d, offset: %d" % (ntp.get_local_time(), ntp.get_offset()))

# Start publishing MQTT-messages
period = 10

wp = WeatherPublisher(name="Weather_Station_esp32_1", prefix="home/greenhouse/weather/esp32-1")
FileLogger.log("Publishing weather measures every %d seconds" % period)

while True:
    wp.busy_publisher(period=period, loops=2)
    ntp.request_time()
    log.log("Time synced from NTP, local: %d, offset: %d" % (ntp.get_local_time(), ntp.get_offset()))


log.close()
