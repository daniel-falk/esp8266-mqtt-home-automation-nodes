from uos import dupterm
from machine import UART

# Initiate the printing to UART
dupterm(UART(0, 115200), 1)
print("Booting...")

# Start the MQTT node client and stuff
import ujson  # noqa
import gc  # noqa

import drivers.wifi as wifi  # noqa
from drivers.simple_ntp import SimpleNTP  # noqa
from drivers.mqtt import MQTTClient  # noqa
from io_controller import IOController  # noqa
from publisher import PublisherCoordinator  # noqa


def main():
    gc.enable()

    # Get the config from json config file
    with open("config.json") as fd:
        config = ujson.loads(fd.read())

    # Disable wifi access point
    wifi.access_point(disable=True)

    # Connect to WIFI and wait for IP
    wifi.connect(config["wifi"]["ssid"], config["wifi"]["password"], True, True)

    gc.collect()

    # Use the NTP to prime the local offset
    ntp = SimpleNTP()
    ntp.request_time()
    print("Time synced from NTP, local: %d, offset: %d" % (ntp.get_local_time(), ntp.get_offset()))

    # Make a MQTT connection
    mqtt = MQTTClient(
            config["mqtt"].get("name"),
            config["mqtt"]["prefix"],
            config["mqtt"]["server"],
            config["mqtt"].get("port", 0))

    # Start an IO controller module (if enabled in config)
    io_conf = config.get("io")
    if io_conf:
        io_controller = IOController(mqtt, io_conf)

    # Start publishing MQTT-messages
    coordinator = PublisherCoordinator(mqtt, config["publisher"])

    # Update the time from NTP every 6th iteration
    coordinator.add_callback(ntp.request_time, divider=30)

    # Check for incoming mqtt messages for the IOContoroller every iteration
    if io_conf:
        coordinator.add_callback(io_controller.iterate, divider=1)

    # The run-call blocks untill an exception is thrown (e.g. ctrl+C)
    print("Free / Available: %d / %d" % (gc.mem_free(), gc.mem_free() + gc.mem_alloc()))
    coordinator.run()


if __name__ == "__main__":
    main()
