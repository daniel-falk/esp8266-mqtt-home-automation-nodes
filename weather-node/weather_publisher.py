from drivers.mqtt import MQTTPublisher
from drivers.read_temp import sensor
from drivers.logging import FileLogger

from time import sleep
from math import isinf

class WeatherPublisher:

    def __init__(self, **kwargs):
        self.pub = MQTTPublisher(**kwargs)


    def busy_publisher(self, period=60, loops=float('inf')):
        cnt = int(loops) if not isinf(loops) else 1
        while cnt > 0:
            tags = ["temperature", "air-pressure", "humidity"]
            units = ["C", "hPa", "%"]
            wdata = sensor.values
            for tag, value, unit in zip(tags, wdata, units):
                data = {
                        "value" : float(value[:-len(unit)]),
                        "unit" : unit
                        }
                self.pub.publish(tag, data, add_ts=True, retain=True)
            sleep(period)
            if not isinf(loops):
                cnt -= 1
