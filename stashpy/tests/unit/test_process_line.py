import unittest
from tornado.testing import AsyncTestCase, gen_test
from tornado import gen

import stashpy
from stashpy.pattern_matching import is_named_re
from .common import TimeStampedMixin

SAMPLE_PARSE = "My name is {name} and I'm {age:d} years old."
SAMPLE_REGEXP = "My name is (?P<name>\w*) and I'm (?P<age>\d*) years old\."

class NamedReTests(unittest.TestCase):

    def test_is_re(self):
        self.assertTrue(is_named_re(SAMPLE_REGEXP))

    def test_is_parse(self):
        self.assertFalse(is_named_re(SAMPLE_PARSE))

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

class MockStream:
    def set_close_callback(*args, **kwargs): pass

class MockIndexer:
    @gen.coroutine
    def index(self, doc):
        if not hasattr(self, 'indexed'):
            self.indexed = []
        self.indexed.append(doc)
        return doc

class ConnectionHandlerTests(AsyncTestCase, TimeStampedMixin):

    @gen_test
    def test_no_parse(self):
        SPEC = {'to_dict':[SAMPLE_PARSE]}
        processor = stashpy.LineProcessor(SPEC)
        indexer = MockIndexer()
        handler = stashpy.ConnectionHandler(MockStream(), None, indexer, processor)
        resp = yield handler.process_line(b"A random line")
        self.assertEqual(len(indexer.indexed), 1)
        self.assertDictEqualWithTimestamp(
            indexer.indexed[0],
            {'message': 'A random line', '@version': 1})


class KitaHandler(stashpy.LineProcessor):

    def for_line(self, line):
        return dict(val='test')

class KitaHandlerTwo(stashpy.LineProcessor):

    TO_DICT = ["My name is {name} and I'm {age:d} years old."]
    TO_FORMAT = {"Her name is {name} and she's {age:d} years old.":
                 {'name_line':"Name is {name}", 'age_line':"Age is {age}"}}

class MainHandlerTests(unittest.TestCase):

    def test_custom_handler(self):
        main = stashpy.MainHandler(
            dict(host='localhost', port=9200),
            processor_class='stashpy.tests.unit.test_process_line.KitaHandler')
        processor = main._load_processor()
        self.assertIsInstance(processor, KitaHandler)
        self.assertDictEqual(processor.for_line('This is a test line'), dict(val='test'))


    def test_spec_handler(self):
        main = stashpy.MainHandler(
            dict(host='localhost', port=9200),
            processor_spec={'to_dict': [SAMPLE_PARSE]})
        processor = main._load_processor()
        self.assertIsInstance(processor, stashpy.LineProcessor)
        self.assertDictEqual(processor.for_line("My name is Julia and I'm 5 years old."),
                             dict(name='Julia', age=5))


    def test_custom_handler_with_specs(self):
        main = stashpy.MainHandler(
            dict(host='localhost', port=9200),
            processor_class='stashpy.tests.unit.test_process_line.KitaHandlerTwo')
        processor = main._load_processor()
        self.assertIsInstance(processor, KitaHandlerTwo)
        self.assertDictEqual(processor.for_line("My name is Juergen and I'm 4 years old."),
                             dict(name='Juergen', age=4))

    def test_no_indexer(self):
        main = stashpy.MainHandler(
            None,
            processor_class='stashpy.tests.unit.test_process_line.KitaHandler')
        processor = main._load_processor()
        self.assertDictEqual(processor.for_line("blah"), dict(val='test'))
