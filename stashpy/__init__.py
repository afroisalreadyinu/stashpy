import sys
import json
import logging
from uuid import uuid4

import tornado.tcpserver
from parse import parse

from tornadoes import ESConnection

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

"My name is {name} and I'm {age:d} years old."

class LineProcessor:

    def __init__(self, spec):
        self.spec = spec

    def __call__(self, line):
        for dict_spec in self.spec['to_dict']:
            dicted = self.to_dict(line, dict_spec)
            if dicted:
                return dicted
        return None

    def to_dict(self, line, dict_spec):
        """Parse the line """
        result = parse(dict_spec, line)
        if result is None:
            return None
        return result.named

class ConnectionHandler:

    def __init__(self, stream, address, server):
        self.stream = stream
        self.address = address
        self.server = server
        self.stream.set_close_callback(self.on_close)
        self.line_processor = LineProcessor(self.SPEC)
        self.loop()

    def loop(self):
        logger.info('Entering loop')
        self.stream.read_until(b"\n", self.process_line)

    def process_line(self, line):
        line = line.decode('utf-8')[:-1]
        logger.info("New line: %s", line)
        result = self.line_processor(line)
        if result:
            logger.info("Match: %s", str(result))
            self.index(result)
        self.loop()

    def index(self, doc):
        doc_id = str(uuid4())
        self.server.es_connection.put(
            index='default',
            type='doc',
            uid=doc_id,
            contents=doc,
            callback=self.index_callback
        )

    def index_callback(self, response):
        logger.info(repr(response))

    def on_close(self):
        logger.info("Connection to %s closed", self.address)



class MainHandler(tornado.tcpserver.TCPServer):


    def __init__(self, *args, **kwargs):
        self.es_connection = ESConnection("localhost", 9200)
        self.connection_class = kwargs.pop('connection_class')
        super().__init__()

    def handle_stream(self, stream, address):
        cn = self.connection_class(stream, address, self)
