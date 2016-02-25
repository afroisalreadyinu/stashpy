import unittest

import stashpy

SAMPLE_PARSE = "My name is {name} and I'm {age:d} years old."
SAMPLE_REGEXP = r"My name is (?P<name>\w*) and I'm (?P<age>\d*) years old."

class NamedReTests(unittest.TestCase):

    def test_is_re(self):
        self.assertTrue(stashpy.is_named_re(SAMPLE_REGEXP))

    def test_is_parse(self):
        self.assertFalse(stashpy.is_named_re(SAMPLE_PARSE))

class LineParserTests(unittest.TestCase):

    def test_re_parser(self):
        parser = stashpy.LineParser(SAMPLE_REGEXP)
        self.assertDictEqual(parser("My name is Aaron and I'm 4 years old"), {'name': 'Aaron', 'age': '4'})



class LineProcessorTests(unittest.TestCase):

    def test_to_dict(self):
        SPEC = {'to_dict':[SAMPLE_PARSE]}
        processor = LineProcessor(SPEC)
        dicted = processor("My name is Valerian and I'm 3 years old.")
        self.assertDictEqual(dicted, {'name': 'Valerian', 'age': 3})


    def test_none_on_no_match(self):
        SPEC = {'to_dict':[SAMPLE_PARSE]}
        processor = LineProcessor(SPEC)
        dicted = processor("I'm not talking to you")
        self.assertIsNone(dicted)


    def test_formatted(self):
        SPEC = {'to_format': {SAMPLE_PARSE: dict(name_and_age="{name}_{age:d}")}}
        processor = LineProcessor(SPEC)
        formatted = processor("My name is Jacob and I'm 3 years old.")
        self.assertDictEqual(formatted, {'name_and_age':'Jacob_3'})


    def test_regexp(self):
        SPEC = {'to_dict':["My name is (?P<name>\w*) and I'm (?P<age>\d*) years old."]}
        processor = LineProcessor(SPEC)
        dicted = processor("My name is Valerian and I'm 3 years old.")
        self.assertDictEqual(dicted, {'name': 'Valerian', 'age': '3'})
