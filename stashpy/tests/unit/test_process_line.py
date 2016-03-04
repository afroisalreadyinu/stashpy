import unittest

import stashpy
from .util import MockESConn, sentinel

SAMPLE_PARSE = "My name is {name} and I'm {age:d} years old."
SAMPLE_REGEXP = "My name is (?P<name>\w*) and I'm (?P<age>\d*) years old\."

class NamedReTests(unittest.TestCase):

    def test_is_re(self):
        self.assertTrue(stashpy.is_named_re(SAMPLE_REGEXP))

    def test_is_parse(self):
        self.assertFalse(stashpy.is_named_re(SAMPLE_PARSE))

class LineParserTests(unittest.TestCase):

    def test_re_parser(self):
        parser = stashpy.LineParser(SAMPLE_REGEXP)
        self.assertDictEqual(parser("My name is Aaron and I'm 4 years old."),
                             {'name': 'Aaron', 'age': '4'})

    def test_parse_parser(self):
        parser = stashpy.LineParser(SAMPLE_PARSE)
        self.assertDictEqual(parser("My name is Aaron and I'm 4 years old."),
                             {'name': 'Aaron', 'age': 4})


class SpecTests(unittest.TestCase):

    def test_dict_spec(self):
        spec = stashpy.DictSpec(stashpy.LineParser(SAMPLE_PARSE))
        self.assertDictEqual(spec("My name is Aaron and I'm 5 years old."),
                             dict({'name': 'Aaron', 'age': 5}))

    def test_format_spec(self):
        spec = stashpy.FormatSpec(stashpy.LineParser(SAMPLE_PARSE),
                                   {'name_and_age': '{name}_{age}'})
        self.assertDictEqual(spec("My name is Aaron and I'm 5 years old."),
                             dict({'name_and_age': 'Aaron_5'}))

class LineProcessorTests(unittest.TestCase):

    def test_to_dict(self):
        SPEC = {'to_dict':[SAMPLE_PARSE]}
        processor = stashpy.LineProcessor(SPEC)
        dicted = processor.for_line("My name is Valerian and I'm 3 years old.")
        self.assertDictEqual(dicted, {'name': 'Valerian', 'age': 3})


    def test_none_on_no_match(self):
        SPEC = {'to_dict':[SAMPLE_PARSE]}
        processor = stashpy.LineProcessor(SPEC)
        dicted = processor.for_line("I'm not talking to you")
        self.assertIsNone(dicted)


    def test_formatted(self):
        SPEC = {'to_format': {SAMPLE_PARSE: dict(name_and_age="{name}_{age:d}")}}
        processor = stashpy.LineProcessor(SPEC)
        formatted = processor.for_line("My name is Jacob and I'm 3 years old.")
        self.assertDictEqual(formatted, {'name_and_age':'Jacob_3'})


    def test_regexp(self):
        SPEC = {'to_dict':["My name is (?P<name>\w*) and I'm (?P<age>\d*) years old."]}
        processor = stashpy.LineProcessor(SPEC)
        dicted = processor.for_line("My name is Valerian and I'm 3 years old.")
        self.assertDictEqual(dicted, {'name': 'Valerian', 'age': '3'})

class KitaHandler(stashpy.LineProcessor):

    def for_line(self, line):
        return dict(val='test')

class ConnectionHandlerTests(unittest.TestCase):

    def test_custom_handler(self):
        main = stashpy.MainHandler(
            dict(host='localhost', port=9200, connection=MockESConn),
            processor_class='stashpy.tests.unit.test_process_line.KitaHandler')
        processor = main._load_processor()
        self.assertIsInstance(processor, KitaHandler)
        self.assertDictEqual(processor.for_line('This is a test line'), dict(val='test'))


    def test_spec_handler(self):
        main = stashpy.MainHandler(
            dict(host='localhost', port=9200, connection=MockESConn),
            processor_spec={'to_dict': [SAMPLE_PARSE]})
        processor = main._load_processor()
        self.assertIsInstance(processor, stashpy.LineProcessor)
        self.assertDictEqual(processor.for_line("My name is Julia and I'm 5 years old."),
                             dict(name='Julia', age=5))