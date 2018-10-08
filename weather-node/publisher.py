from time import sleep

from drivers.logging import FileLogger
from drivers.mqtt import MQTTPublisher

class Callback():

    def __init__(self, divider, callback, **kwargs):
        self.divider = divider
        self.callback = callback
        self.kwargs = kwargs

    def call(self):
        self.callback(**self.kwargs)


class PublisherCoordinator():

    def __init__(self, config):
        self.config = config
        self.callbacks = []
        self.iterator = 0
        self.max_iterator = 1

        self.add_mqtt_callbacks()


    def add_callback(self, callback, divider=1, **kwargs):
        self.callbacks.append(Callback(divider, callback, **kwargs))


    def add_mqtt_callbacks(self):
        config = self.config
        mqtt = MQTTPublisher(name=config["publisher"]["name"], prefix=config["publisher"]["prefix"])

        # Add weather sensor if specified in config file
        try:
            divider = config["publisher"]["data"]["weather"]["divider"]
            from weather_publisher import WeatherPublisher
            wp = WeatherPublisher("weather", mqtt_publisher=mqtt)
            self.add_callback(wp.publish, divider)
            period = self.config["publisher"]["period"] * divider
            FileLogger.log("Publishing weather measures every %d seconds" % period)
        except KeyError:
            pass

        # Add weather sensor if specified in config file
        try:
            divider = config["publisher"]["data"]["soil"]["divider"]
            from soil_publisher import SoilPublisher
            sp = SoilPublisher("soil", mqtt_publisher=mqtt)
            self.add_callback(sp.publish, divider)
            period = self.config["publisher"]["period"] * divider
            FileLogger.log("Publishing soil moisture measures every %d seconds" % period)
        except KeyError:
            pass

        # Add temperature sensor if specified in config file
        try:
            divider = config["publisher"]["data"]["temperature"]["divider"]
            pin = config["publisher"]["data"]["temperature"]["GPIO"]
            from ds18x20_publisher import DS18X20Publisher
            tp = DS18X20Publisher(postfix="temperature", mqtt_publisher=mqtt, pin=pin)
            self.add_callback(tp.publish, divider)
            period = self.config["publisher"]["period"] * divider
            FileLogger.log("Publishing temperature measures every %d seconds" % period)
        except KeyError:
            pass



    def run(self):
        while True:
            self.iterator += 1

            for cb in self.callbacks:
                if self.iterator % cb.divider == 0:
                    cb.call()

            sleep(self.config["publisher"]["period"])
