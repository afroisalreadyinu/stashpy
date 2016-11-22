from stashpy.processor import LineProcessor
import unittest

class PatternTest(unittest.TestCase):

    def process_to_dict(self, to_dict, logline):
        return LineProcessor(specs=dict(to_dict=to_dict)).for_line(logline)

    def process_to_format(self, to_format, logline):
        return LineProcessor(specs=dict(to_format=to_format)).for_line(logline)

    def process_spec(self, spec, logline):
        return LineProcessor(specs=spec).for_line(logline)
