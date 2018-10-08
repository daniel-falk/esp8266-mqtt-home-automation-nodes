from machine import Pin
from ds18x20 import DS18X20
from onewire import OneWire
from binascii import hexlify

from publisher import BasePublisher
from drivers.logging import FileLogger


class DS18X20Publisher(BasePublisher):

    def __init__(self, postfix, pin, **kwargs):
        super().__init__(postfix, **kwargs)
        self.pin = Pin(pin)
        self.onewire = OneWire(self.pin)
        self.sensor = DS18X20(self.onewire)
        self.roms = self.sensor.scan()
        self.initialized = False  # Sensor conversion takes 700mS, always lag one iteration behind.
        FileLogger.log("Found %d ds18x20 sensors" % len(self.roms))

    def publish(self):
        # Lag one conversion behind to give atleast 700mS notice...
        self.sensor.convert_temp()
        if not self.initialized:
            self.initialized = True
            return
        data = {hexlify(rom).decode('ascii'): self.sensor.read_temp(rom) for rom in self.roms}
        self.pub.publish(data, postfix=self.postfix, add_ts=True, retain=True)
