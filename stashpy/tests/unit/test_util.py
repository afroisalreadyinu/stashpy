import unittest

from stashpy.handler import RotatingCounter

class DummyLogger:
    def __init__(self):
        self.logs = []

    def info(self, line, *args):
        self.logs.append(line.format(*args))


class RotatingHandlerTests(unittest.TestCase):

    def test_resets_at_max(self):
        counter = RotatingCounter(2, "{}", DummyLogger())
        for _ in range(2):
            counter.inc()
        self.assertEqual(counter.current, 0)


    def test_logs_message(self):
        logger = DummyLogger()
        counter = RotatingCounter(2, "Maximum: {}", logger)
        for _ in range(2):
            counter.inc()
        self.assertEqual(len(logger.logs), 1)
        self.assertEqual(logger.logs[0], "Maximum: 2")
