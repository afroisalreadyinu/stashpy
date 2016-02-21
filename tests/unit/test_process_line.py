import unittest

from stashpy import LineProcessor

SPEC = {'to_dict':["My name is {name} and I'm {age:d} years old."]}

class LineProcessorTests(unittest.TestCase):

    def test_to_dict(self):
        processor = LineProcessor(SPEC)
        dicted = processor("My name is Valerian and I'm 3 years old.")
        self.assertDictEqual(dicted, {'name': 'Valerian', 'age': 3})


    def test_none_on_no_match(self):
        processor = LineProcessor(SPEC)
        dicted = processor("I'm not talking to you")
        self.assertIsNone(dicted)
