from publisher import BasePublisher
from drivers.read_temp import sensor


class WeatherPublisher(BasePublisher):

    def publish(self):
        try:
            wdata = sensor.values
        except OSError:
            print("Failed to read weather sensor info... OSERROR")
            return
        tags = ["temperature", "air-pressure", "humidity"]
        units = ["C", "hPa", "%"]
        data = {tag: float(value[:-len(unit)]) for tag, value, unit in zip(tags, wdata, units)}
        self.pub.publish(data, postfix=self.postfix, add_ts=True, retain=True)
