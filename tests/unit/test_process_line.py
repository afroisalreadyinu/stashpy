import unittest

from stashpy import LineProcessor


class LineProcessorTests(unittest.TestCase):

    def test_to_dict(self):
        SPEC = {'to_dict':["My name is {name} and I'm {age:d} years old."]}
        processor = LineProcessor(SPEC)
        dicted = processor("My name is Valerian and I'm 3 years old.")
        self.assertDictEqual(dicted, {'name': 'Valerian', 'age': 3})


    def test_none_on_no_match(self):
        SPEC = {'to_dict':["My name is {name} and I'm {age:d} years old."]}
        processor = LineProcessor(SPEC)
        dicted = processor("I'm not talking to you")
        self.assertIsNone(dicted)


    def test_formatted(self):
        SPEC = {'to_format':
                {"My name is {name} and I'm {age:d} years old.":
                 dict(name_and_age="{name}_{age:d}")}}
        processor = LineProcessor(SPEC)
        formatted = processor("My name is Jacob and I'm 3 years old.")
        self.assertDictEqual(formatted, {'name_and_age':'Jacob_3'})
