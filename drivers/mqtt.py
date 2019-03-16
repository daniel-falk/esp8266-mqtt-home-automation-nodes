import machine
import gc
from json import dumps

from .wifi import get_ip, get_mac
from .simple_ntp import SimpleNTP

from umqtt.robust import MQTTClient as RobustMQTTClient
from umqtt.simple import MQTTException


class SuperRobustMQTTClient(RobustMQTTClient):
    MAX_RETRIES = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect(self, *args, **kwargs):
        self._try_hard(super().connect, *args, **kwargs)
        print("Connected to MQTT")

    def reconnect(self):
        self._try_hard(super().connect, False)
        print("Reconnected to MQTT")

    def _try_hard(self, func, *args, **kwargs):
        i = 0
        while 1:
            try:
                return func(*args, **kwargs)
            except (OSError, MQTTException) as e:
                print("Connect error: %s" % str(e))
                i += 1
                self.delay(i)
                if i > self.MAX_RETRIES:
                    print("Can't connect to MQTT, hard rebooting..")
                    machine.reset()


class MQTTClient(SuperRobustMQTTClient):

    TOPIC_COMMAND = "commands".encode("utf-8")
    TOPIC_INFO = "info".encode("utf-8")

    def __init__(self, name, prefix, server, port):
        self.name = name or get_mac()
        self.prefix = prefix.encode("utf-8")
        self.server = server
        self.port = port

        super().__init__(self.name, self.server, self.port)
        self.connect()

        self._pub_info("ip", get_ip())
        self._pub_info("connected", "%d" % SimpleNTP.get_local_time())

        self.topic_types = [None, self.TOPIC_COMMAND, self.TOPIC_INFO]

    def publish(self, data, postfix=None, add_ts=False, retain=False):
        now = SimpleNTP.get_local_time()
        if add_ts:
            data["time"] = now

        if postfix:
            topic = b"/".join([self.prefix, postfix.encode("utf-8")])
        else:
            topic = self.prefix

        payload = data if isinstance(data, str) else dumps(data)
        super().publish(topic, payload.encode("utf-8"), retain)
        self._pub_info("last_update", "%d" % now)
        self._pub_info("free_mem", "%d" % gc.mem_free())
        self._pub_info("tot_mem", "%d" % (gc.mem_free() + gc.mem_alloc()))


    def subscribe(self, name, type=None, qos=1):
        if type not in self.topic_types:
            raise ValueError("Unknown subscription type: {}".format(type))
        topic = b"/".join([x for x in [type, self.prefix, name.encode("utf-8")] if x is not None])
        super().subscribe(topic, qos=qos)

    def _pub_info(self, name, msg, retain=True):
        topic = b"/".join([self.TOPIC_INFO, name.encode("utf-8"), self.prefix])
        super().publish(topic, msg.encode("utf-8"), retain)
