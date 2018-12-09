from time import sleep
from abc import ABCMeta, abstractmethod
from drivers.mqtt import MQTTClient


class BasePublisher():
    """Abstract class to inherit when building sensor specific publishers"""
    __metaclass__ = ABCMeta

    def __init__(self, postfix, mqtt_publisher=None, **kwargs):
        self.postfix = postfix
        if mqtt_publisher is None:
            self.pub = MQTTClient(**kwargs)
        else:
            self.pub = mqtt_publisher

    @abstractmethod
    def publish(self):
        pass


class Callback():
    """Simple callback structure for registered callbacks"""
    def __init__(self, divider, callback, **kwargs):
        self.divider = divider
        self.callback = callback
        self.kwargs = kwargs

    def call(self):
        self.callback(**self.kwargs)


class PublisherCoordinator():
    """Coordinator for sensor specific publishers"""
    def __init__(self, mqtt, config):
        self.mqtt = mqtt
        self.config = config
        self.callbacks = []
        self.iterator = 0
        self.max_iterator = 1

        self.add_mqtt_callbacks()

    def add_callback(self, callback, divider=1, **kwargs):
        self.callbacks.append(Callback(divider, callback, **kwargs))

    def add_mqtt_callbacks(self):
        config = self.config
        mqtt = self.mqtt

        # Add weather sensor if specified in config file
        try:
            divider = config["data"]["weather"]["divider"]
            from weather_publisher import WeatherPublisher
            wp = WeatherPublisher("weather", mqtt_publisher=mqtt)
            self.add_callback(wp.publish, divider)
            period = self.config["period"] * divider
            print("Publishing weather measures every %d seconds" % period)
        except KeyError:
            pass

        # Add weather sensor if specified in config file
        try:
            divider = config["data"]["soil"]["divider"]
            from soil_publisher import SoilPublisher
            sp = SoilPublisher("soil", mqtt_publisher=mqtt)
            self.add_callback(sp.publish, divider)
            period = self.config["period"] * divider
            print("Publishing soil moisture measures every %d seconds" % period)
        except KeyError:
            pass

        # Add temperature sensor if specified in config file
        try:
            divider = config["data"]["temperature"]["divider"]
            pin = config["data"]["temperature"]["GPIO"]
            from ds18x20_publisher import DS18X20Publisher
            tp = DS18X20Publisher(postfix="temperature", mqtt_publisher=mqtt, pin=pin)
            self.add_callback(tp.publish, divider)
            period = self.config["period"] * divider
            print("Publishing temperature measures every %d seconds" % period)
        except KeyError:
            pass

    def run(self):
        while True:
            self.iterator += 1

            for cb in self.callbacks:
                if self.iterator % cb.divider == 0:
                    cb.call()

            sleep(self.config["period"])
