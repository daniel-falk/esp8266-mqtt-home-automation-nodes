from publisher import BasePublisher
from drivers.read_temp import sensor


class WeatherPublisher(BasePublisher):

    def publish(self):
        tags = ["temperature", "air-pressure", "humidity"]
        units = ["C", "hPa", "%"]
        wdata = sensor.values
        data = {tag: float(value[:-len(unit)]) for tag, value, unit in zip(tags, wdata, units)}
        self.pub.publish(data, postfix=self.postfix, add_ts=True, retain=True)
