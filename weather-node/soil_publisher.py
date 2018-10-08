import machine

from publisher import BasePublisher


class SoilPublisher(BasePublisher):

    def __init__(self, postfix, **kwargs):
        super().__init__(postfix, **kwargs)
        self.adc = machine.ADC(0)

    def publish(self):
        data = {"moisture1": self.adc.read() / 1024}
        self.pub.publish(data, postfix=self.postfix, add_ts=True, retain=True)
