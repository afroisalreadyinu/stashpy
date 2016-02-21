import unittest

from stashpy import LineProcessor

class LineProcessorTests(unittest.TestCase):

    def test_to_dict(self):
        spec = {'to_dict':["My name is {name} and I'm {age:d} years old."]}
        processor = LineProcessor(spec)
        dicted = processor("My name is Valerian and I'm 3 years old.")
        self.assertDictEqual(dicted, {'name': 'Valerian', 'age': 3})
