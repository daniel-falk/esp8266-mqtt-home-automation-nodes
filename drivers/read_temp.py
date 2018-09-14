from .bme280 import BME280

import machine

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
sensor = BME280(i2c=i2c)
