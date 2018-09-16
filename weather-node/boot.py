
# Initiate the logging and printing to UART

from drivers.logging import FileLogger
import uos
import machine

uos.dupterm(machine.UART(0, 115200), 1)

log = FileLogger.get_instance()
log.stdout = True

log.log("Boot start")

# Start the MQTT node client and stuff

import sys
import machine
from time import sleep
import ujson

import drivers.wifi as wifi
from weather_publisher import WeatherPublisher
from drivers.simple_ntp import SimpleNTP

# Get the config from json config file
config = ujson.loads(open("config.json").read())

# Disable wifi access point
wifi.access_point(disable=True)

# Connect to WIFI and wait for IP
wifi.connect(**config["wifi"], wait=True, allow_restart=True)

# Use the NTP to prime the local offset
ntp = SimpleNTP()
ntp.request_time()
log.log("Time synced from NTP, local: %d, offset: %d" % (ntp.get_local_time(), ntp.get_offset()))

# Start publishing MQTT-messages
period = config["publisher"]["period"]
wp = WeatherPublisher(name=config["publisher"]["name"], prefix=config["publisher"]["prefix"])
FileLogger.log("Publishing weather measures every %d seconds" % period)

while True:
    wp.busy_publisher(period=period, loops=6)
    ntp.request_time()

log.close()
