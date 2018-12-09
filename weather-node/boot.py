import uos
import machine

# Initiate the printing to UART
uos.dupterm(machine.UART(0, 115200), 1)
print("Booting...")

# Start the MQTT node client and stuff
import sys  # noqa
import machine  # noqa
import ujson  # noqa

import drivers.wifi as wifi  # noqa
from drivers.simple_ntp import SimpleNTP  # noqa
from drivers.mqtt import MQTTClient  # noqa
from io_controller import IOController  # noqa
from publisher import PublisherCoordinator  # noqa

# Get the config from json config file
config = ujson.loads(open("config.json").read())

# Disable wifi access point
wifi.access_point(disable=True)

# Connect to WIFI and wait for IP
wifi.connect(wait=True, allow_restart=True, **config["wifi"])

# Use the NTP to prime the local offset
ntp = SimpleNTP()
ntp.request_time()
print("Time synced from NTP, local: %d, offset: %d" % (ntp.get_local_time(), ntp.get_offset()))

# Make a MQTT connection
mqtt = MQTTClient(
        name=config["mqtt"].get("name"),
        prefix=config["mqtt"]["prefix"],
        server=config["mqtt"]["server"])

# Start an IO controller module (if enabled in config)
io_conf = config.get("io")
if io_conf:
    io_controller = IOController(mqtt, io_conf)

# Start publishing MQTT-messages
coordinator = PublisherCoordinator(mqtt, config["publisher"])

# Update the time from NTP every 6th iteration
coordinator.add_callback(ntp.request_time, divider=6)

# Check for incoming mqtt messages for the IOContoroller every iteration
if io_conf:
    coordinator.add_callback(io_controller.iterate, divider=1)

# The run-call blocks untill an exception is thrown (e.g. ctrl+C)
coordinator.run()
