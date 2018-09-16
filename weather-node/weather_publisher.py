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
            data = {tag: float(value[:-len(unit)]) for tag, value, unit in zip(tags, wdata, units)}
            self.pub.publish(data, postfix="weather", add_ts=True, retain=True)
            sleep(period)
            if not isinf(loops):
                cnt -= 1
