import sys
import json
import logging
from uuid import uuid4
import copy
import re
from datetime import datetime

from tornado import gen
import tornado.tcpserver
import parse

from tornadoes import ESConnection

logger = logging.getLogger(__name__)

#parsing re's with re's. i'm going to hell for this.
NAMED_RE_RE = re.compile(r"\(\?P<\w*>.*?\)")

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

    def __init__(self, specs):
        self.dict_specs = [DictSpec(LineParser(spec))
                           for spec in specs.get('to_dict', [])]
        self.format_specs = [FormatSpec(LineParser(format_spec), output_spec)
                             for format_spec, output_spec in specs.get('to_format', {}).items()]


    def __call__(self, line):
        for dict_spec in self.dict_specs:
            dicted = dict_spec(line)
            if dicted:
                return dicted
        for format_spec in self.format_specs:
            formatted = format_spec(line)
            if formatted:
                return formatted
        return None

class ESIndexer:

    def __init__(self, es_host, es_port, index_pattern="stashpy-%Y-%m-%d", connection=ESConnection):
        self.es_connection = connection(es_host, es_port)
        self.index_pattern = index_pattern

    def index(self, doc):
        doc_id = str(uuid4())
        index = datetime.strftime(datetime.now(), self.index_pattern)
        return self.es_connection.put(
            index=index,
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
    def on_close(self):
        #Close es connection?
        logger.info("Connection to %s closed", self.address)
        yield []



class MainHandler(tornado.tcpserver.TCPServer):


    def __init__(self, *args, **kwargs):
        es_host = kwargs.pop('es_host')
        es_port = kwargs.pop('es_port')
        self.connection_class = kwargs.pop('connection_class')
        super().__init__()
        logger.info("Stashpy started, accepting connections on {}:{}".format(
            'localhost',
            8888))

    @gen.coroutine
    def handle_stream(self, stream, address):
        cn = self.connection_class(stream, address, self)
        yield cn.on_connect()
