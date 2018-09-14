from .simple_ntp import SimpleNTP

class FileLogger:
    __instance = None


    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls()
        return cls.__instance


    @classmethod
    def log(cls, *args, **kwargs):
        cls.get_instance()._log(*args, **kwargs)


    def __init__(self):
        if FileLogger.__instance:
            raise Exception("Singleton should be initiated with get_instance()")

        self.stdout = False

        self.f = open("log.txt", "a")
        self.f.write("----------------")
        self.f.flush()

        self.ntp = SimpleNTP()

        FileLogger.__instance = self


    def close(self):
        self.f.close()


    def _log(self, txt):
        if self.stdout:
            print(txt)
        self.f.write("%d: %s\n" % (self.ntp.get_local_time(), txt))
        self.f.flush()
