import sys
import json
import logging
from uuid import uuid4
import copy

from tornado import gen
import tornado.tcpserver
from parse import parse

from tornadoes import ESConnection

logger = logging.getLogger(__name__)

class LineProcessor:

    def __init__(self, spec):
        self.spec = spec

    def __call__(self, line):
        for dict_spec in self.spec.get('to_dict', []):
            dicted = self.to_dict(line, dict_spec)
            if dicted:
                return dicted
        for format_spec,output_spec in self.spec.get('to_format', {}).items():
            formatted = self.to_format(line, format_spec, output_spec)
            if formatted:
                return formatted
        return None

    def to_dict(self, line, dict_spec):
        """Parse the line """
        result = parse(dict_spec, line)
        if result is None:
            return None
        return result.named

    def _format_dict(self, out_dict, value_dict):
        for key,val in out_dict.items():
            if isinstance(key, dict):
                self._format_dict(val, value_dict)
            else:
                import pdb;pdb.set_trace()
                out_dict[key] = val.format(**value_dict)


    def to_format(self, line, format_spec, output_spec):
        """Parse the line """
        result = parse(format_spec, line)
        if result is None:
            return None
        output = copy.deepcopy(output_spec)
        self._format_dict(output, result.named)
        return output

class ConnectionHandler:

    def __init__(self, stream, address, server):
        self.stream = stream
        self.address = address
        self.server = server
        self.stream.set_close_callback(self.on_close)
        self.line_processor = LineProcessor(self.SPEC)
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
        result = self.line_processor(line)
        if result:
            logger.info("Match: %s", str(result))
            yield self.index(result)

    @gen.coroutine
    def index(self, doc):
        doc_id = str(uuid4())
        yield self.server.es_connection.put(
            index='default',
            type='doc',
            uid=doc_id,
            contents=doc,
            callback=self.index_callback
        )

    def index_callback(self, response):
        if 200 <= response.status < 300:
            logger.info("Successfully indexed doc, id: {}".format(response.effective_url))
        else:
            logger.warn("Index request returned response {}, reason: {}".format(
                response.code,
                response.reason))

    @gen.coroutine
    def on_close(self):
        logger.info("Connection to %s closed", self.address)
        yield []



class MainHandler(tornado.tcpserver.TCPServer):


    def __init__(self, *args, **kwargs):
        es_host = kwargs.pop('es_host')
        es_port = kwargs.pop('es_port')
        self.es_connection = ESConnection(es_host, es_port)
        self.connection_class = kwargs.pop('connection_class')
        super().__init__()
        logger.info("Stashpy started, accepting connections on {}:{}".format(
            'localhost',
            8888))

    @gen.coroutine
    def handle_stream(self, stream, address):
        cn = self.connection_class(stream, address, self)
        yield cn.on_connect()
