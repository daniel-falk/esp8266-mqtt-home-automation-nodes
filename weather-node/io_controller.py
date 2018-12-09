import machine


class IOController:

    def __init__(self, mqtt, devices):
        self.mqtt = mqtt
        self.devices = devices

        if mqtt.cb is not None:
            raise ValueError("MQTT callback is already set: Not supported by IOController...")

        mqtt.set_callback(self._callback)
        self.io = {}
        for device, gpio in devices.items():
            mqtt.subscribe(type=mqtt.TOPIC_COMMAND, name=device)
            self.io[device] = machine.Pin(gpio, machine.Pin.OUT)

        self.cb_flag = False

    def _callback(self, topic, message):
        device = topic.decode("utf-8").split("/")[-1]
        self.io[device].value(1 if message == b'on' else 0)
        self.mqtt.publish(message.decode("utf-8"), postfix=device)
        self.cb_flag = True

    def iterate(self):
        '''Process mqtt messages atleast once, stop when callback wasn't called
        '''
        while True:
            self.mqtt.check_msg()
            if not self.cb_flag:
                break
            self.cb_flag = False
