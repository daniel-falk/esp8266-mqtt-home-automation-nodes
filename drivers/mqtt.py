from .wifi import get_ip, get_mac
from .simple_ntp import SimpleNTP
from .logging import FileLogger


from umqtt.robust import MQTTClient as RobustMQTTClient
from json import dumps
import utime
import machine

class MQTTClient(RobustMQTTClient):
    MAX_RETRIES = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def connect(self, *args, **kwargs):
        self._try_hard(super().connect, *args, **kwargs)
        FileLogger.log("Connected")


    def reconnect(self):
        self._try_hard(super().connect, False)
        FileLogger.log("Reconnected")


    def _try_hard(self, func, *args, **kwargs):
        i = 0
        while 1:
            try:
                return func(*args, **kwargs)
            except OSError as e:
                i += 1
                FileLogger.log("%s, i is now %d" % (e, i))
                self.delay(i)
                if i > self.MAX_RETRIES:
                    FileLogger.log("I'm done, hard rebooting..")
                    machine.reset()


class MQTTPublisher:

    def __init__(self, name, prefix, server):
        self.name = name or get_mac()
        self.prefix = prefix.encode("utf-8")
        self.server = server

        self.ntp = SimpleNTP()

        self.client = MQTTClient(self.name, self.server)
        self.client.connect()

        self._pub_info("ip", get_ip())
        self._pub_info("connected", "%d" % self.ntp.request_time())


    def publish(self, data, postfix=None, add_ts=False, retain=False):
        now = self.ntp.get_local_time()
        if add_ts:
            data["time"] = now

        if postfix:
            topic = b"/".join([self.prefix, postfix.encode("utf-8")])
        else:
            topic = self.prefix

        self.client.publish(topic, dumps(data).encode("utf-8"), retain)
        self._pub_info("last_update", "%d" % now)


    def _pub_info(self, name, msg, retain=True):
        self.client.publish(b"/".join([b"info", name.encode("utf-8"), self.prefix]), msg.encode("utf-8"), retain)
