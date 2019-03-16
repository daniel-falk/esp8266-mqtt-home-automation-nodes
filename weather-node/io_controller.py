import machine


class Device:
    def __init__(self, name, info_dict):
        self.name = name
        self.timeout = info_dict.get("timeout")
        self.io = machine.Pin(info_dict["gpio"], machine.Pin.OUT)
        self.default = info_dict.get("default", 0)
        self.io.value(self.default)
        if self.timeout:
            from drivers.simple_ntp import SimpleNTP
            self.get_time = SimpleNTP.get_local_time
            self.update_time = 0

    def set_from_string(self, string):
        self.update_time = self.get_time()
        if string in ["ON", "on", "On"]:
            self.io.value(1)
        else:
            self.io.value(0)

    def monitor_timeout(self):
        if self.timeout:
            if self.io.value() != self.default or not self.update_time:
                now = self.get_time()
                if self.update_time + self.timeout < now:
                    self.io.value(self.default)
                    return self.default
        return None


class IOController:

    def __init__(self, mqtt, devices):
        self.mqtt = mqtt
        if mqtt.cb is not None:
            raise ValueError("MQTT callback is already set: Not supported by IOController...")
        mqtt.set_callback(self._callback)
        self.devices = {}
        for device_name, info in devices.items():
            mqtt.subscribe(type=mqtt.TOPIC_COMMAND, name=device_name)
            self.devices[device_name] = Device(device_name, info)
        self.cb_flag = False

    def _callback(self, topic, message):
        message = message.decode('utf-8')
        device_name = topic.decode("utf-8").split("/")[-1]
        self.devices[device_name].set_from_string(message)
        self.mqtt.publish(message, postfix=device_name)
        self.cb_flag = True

    def iterate(self):
        '''Process mqtt messages atleast once, stop when callback wasn't called
        '''
        for device in self.devices.values():
            new_val = device.monitor_timeout()
            if new_val is not None:
                self.mqtt.publish("off" if new_val == 0 else "on", postfix=device.name)
        while True:
            self.mqtt.check_msg()
            if not self.cb_flag:
                break
            self.cb_flag = False
