
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
import ujson

import drivers.wifi as wifi
from drivers.simple_ntp import SimpleNTP
from publisher import PublisherCoordinator

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
# Update the time from NTP every 6th iteration
# The run-call blocks untill an exception is thrown (e.g. ctrl+C)
coordinator = PublisherCoordinator(config)
coordinator.add_callback(ntp.request_time, divider=6)
coordinator.run()

# Clean up..
log.close()
