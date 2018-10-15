import unittest


class TestWeatherNode(unittest.TestCase):

    def test_logger(self):
        from drivers.logging import FileLogger
        log = FileLogger.get_instance()
        log.stdout = True
        log.log("Test logger")


if __name__ == '__main__':
    unittest.main()
