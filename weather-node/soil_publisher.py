import machine

from drivers.mqtt import MQTTPublisher
from drivers.logging import FileLogger

class SoilPublisher:

    def __init__(self, postfix, mqtt_publisher=None, **kwargs):
        self.postfix = postfix
        self.adc = machine.ADC(0)

        if mqtt_publisher is None:
            self.pub = MQTTPublisher(**kwargs)
        else:
            self.pub = mqtt_publisher


    def publish(self):
        data = {"moisture1": self.adc.read() / 1024}
        self.pub.publish(data, postfix=self.postfix, add_ts=True, retain=True)
