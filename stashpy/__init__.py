import sys
import json
import logging
from uuid import uuid4
import copy
import re
from datetime import datetime
import importlib

from tornado import gen
import tornado.tcpserver
from tornado.httpclient import HTTPRequest
import parse

logger = logging.getLogger(__name__)

#parsing re's with re's. i'm going to hell for this.
NAMED_RE_RE = re.compile(r"\(\?P<\w*>.*?\)")

DEFAULT_PORT = 8899
DEFAULT_ADDRESS = '0.0.0.0'

def is_named_re(maybe_re):
    found = NAMED_RE_RE.findall(maybe_re)
    return found

class LineParser:

    def __init__(self, spec):
        if is_named_re(spec):
            self.re = re.compile(spec)
            self.parse = None
        else:
            self.re = None
            self.parse = parse.compile(spec)

    def __call__(self, line):
        if self.re:
            match = self.re.match(line)
            if match is None:
                return None
            return {group_name:match.group(group_name)
                    for group_name in self.re.groupindex}
        match = self.parse.parse(line)
        if match is None:
            return None
        return match.named

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
        if specs:
            self.dict_specs = [DictSpec(LineParser(spec))
                               for spec in specs.get('to_dict', [])]
            self.format_specs = [FormatSpec(LineParser(format_spec), output_spec)
                                 for format_spec, output_spec in specs.get('to_format', {}).items()]

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

class ESIndexer:

    def __init__(self, host, port, index_pattern="stashpy-%Y-%m-%d", doc_type='doc'):
        self.base_url = 'http://{}:{}'.format(host, port)
        self.client = tornado.httpclient.AsyncHTTPClient()
        self.index_pattern = index_pattern
        self.doc_type = doc_type

    def _create_request(self, doc):
        doc_id = str(uuid4())
        if '_index_' in doc:
            index = datetime.strftime(datetime.now(), doc['_index_'])
            if '{' in index and '}' in index:
                index = index.format(**doc)
            doc.pop('_index_')
        else:
            index = datetime.strftime(datetime.now(), self.index_pattern)
        url = self.base_url + "/{}/{}/{}".format(index, self.doc_type, doc_id)
        return HTTPRequest(url, method='POST', headers=None, body=json.dumps(doc))

    @gen.coroutine
    def index(self, doc):
        request = self._create_request(doc)
        response = yield self.client.fetch(request)
        if 200 <= response.code < 300:
            logger.info("Successfully indexed doc, url: {}".format(
                response.effective_url))
        else:
            logger.warn("Index request returned response {}, reason: {}".format(
                response.code,
                response.reason))


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
            8888))
        io_loop = tornado.ioloop.IOLoop.current()
        if not io_loop._running:
            io_loop.start()
