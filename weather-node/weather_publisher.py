from drivers.mqtt import MQTTPublisher
from drivers.read_temp import sensor

class WeatherPublisher:

    def __init__(self, postfix, mqtt_publisher=None, **kwargs):
        self.postfix = postfix

        if mqtt_publisher is None:
            self.pub = MQTTPublisher(**kwargs)
        else:
            self.pub = mqtt_publisher


    def publish(self):
        tags = ["temperature", "air-pressure", "humidity"]
        units = ["C", "hPa", "%"]
        wdata = sensor.values
        data = {tag: float(value[:-len(unit)]) for tag, value, unit in zip(tags, wdata, units)}
        self.pub.publish(data, postfix=self.postfix, add_ts=True, retain=True)
