import sys
import json
import logging
import copy
import importlib

from tornado import gen
import tornado.tcpserver

from .indexer import ESIndexer
from .pattern_matching import LineParser

logger = logging.getLogger(__name__)

DEFAULT_PORT = 8899
DEFAULT_ADDRESS = '0.0.0.0'

class DictSpec:

    def __init__(self, parser):
        self.parser = parser

    def __call__(self, line):
        return self.parser(line)

class FormatSpec:

    def __init__(self, parser, out_format):
        self.parser = parser
        self.out_format = out_format

    def __call__(self, line):
        """Parse the line """
        result = self.parser(line)
        if result is None:
            return None
        output = copy.deepcopy(self.out_format)
        self._format_dict(output, result)
        return output

    def _format_dict(self, out_dict, value_dict):
        for key,val in out_dict.items():
            if isinstance(key, dict):
                self._format_dict(val, value_dict)
            else:
                out_dict[key] = val.format(**value_dict)


class LineProcessor:

    def __init__(self, specs=None):
        to_dict_specs, to_format_specs = [], {}
        if specs:
            to_dict_specs = specs.get('to_dict', [])
            to_format_specs = specs.get('to_format', {})
        else:
            if hasattr(self, 'TO_DICT'):
                to_dict_specs = self.TO_DICT
            if hasattr(self, 'TO_FORMAT'):
                to_format_specs = self.TO_FORMAT
        self.dict_specs = [DictSpec(LineParser(spec))
                           for spec in to_dict_specs]
        self.format_specs = [FormatSpec(LineParser(format_spec), output_spec)
                             for format_spec, output_spec in to_format_specs.items()]


    def do_dict_specs(self, line):
        for dict_spec in self.dict_specs:
            dicted = dict_spec(line)
            if dicted:
                return dicted
        return None

    def do_format_specs(self, line):
        for format_spec in self.format_specs:
            formatted = format_spec(line)
            if formatted:
                return formatted
        return None

    def for_line(self, line):
        dict_result = self.do_dict_specs(line)
        if dict_result:
            return dict_result
        format_result = self.do_format_specs(line)
        if format_result:
            return format_result
        return None

class ConnectionHandler:

    def __init__(self, stream, address, indexer, line_processor):
        self.stream = stream
        self.address = address
        self.indexer = indexer
        self.line_processor = line_processor
        self.stream.set_close_callback(self.on_close)
        logger.info("Accepted connection from {}".format(address))

    @gen.coroutine
    def on_connect(self):
        yield self.dispatch_client()

    @gen.coroutine
    def dispatch_client(self):
        try:
            while True:
                line = yield self.stream.read_until(b"\n")
                yield self.process_line(line)
        except tornado.iostream.StreamClosedError:
            pass

    @gen.coroutine
    def process_line(self, line):
        line = line.decode('utf-8')[:-1]
        logger.debug("New line: %s", line)
        result = self.line_processor.for_line(line)
        if result:
            logger.info("Match: %s", str(result))
            result['message'] = line
            result['@version'] = 1
            yield self.indexer.index(result)



    @gen.coroutine
    def on_close(self):
        #Close es connection?
        logger.info("Connection to %s closed", self.address)
        yield []



class MainHandler(tornado.tcpserver.TCPServer):


    def __init__(self, es_config, processor_spec=None, processor_class=None):
        assert processor_spec is not None or processor_class is not None
        self.processor_spec = processor_spec
        self.processor_class = processor_class
        self.es_config = es_config
        super().__init__()

    def _load_processor(self):
        if self.processor_spec:
            line_processor = LineProcessor(self.processor_spec)
        else:
            module_name,class_name = self.processor_class.rsplit('.', 1)
            module = importlib.import_module(module_name)
            _class = getattr(module, class_name)
            line_processor = _class()
        return line_processor

    @gen.coroutine
    def handle_stream(self, stream, address):
        cn = ConnectionHandler(stream, address,
                               ESIndexer(**self.es_config),
                               self._load_processor())
        yield cn.on_connect()


DEFAULT_ES_CONF = {'host': 'localhost', 'port': 9200 }

class App:
    def __init__(self, config):
        assert 'processor_spec' in config or 'processor_class' in config
        self.config = config
        self.main = MainHandler(es_config=config.get('es_config', DEFAULT_ES_CONF),
                                processor_spec=config.get('processor_spec'),
                                processor_class=config.get('processor_class'))

    def run(self):
        port = self.config.get('port', DEFAULT_PORT)
        self.main.listen(port, address=DEFAULT_ADDRESS)
        logger.info("Stashpy started, accepting connections on {}:{}".format(
            'localhost',
            port))
        io_loop = tornado.ioloop.IOLoop.current()
        if not io_loop._running:
            io_loop.start()
