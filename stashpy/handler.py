import importlib
import logging
from datetime import datetime
import pytz

from tornado import gen
import tornado.tcpserver

from .indexer import ESIndexer
from .processor import LineProcessor

logger = logging.getLogger(__name__)

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
        line = line.decode('utf-8').rstrip('\n')
        logger.debug("New line: %s", line)
        result = self.line_processor.for_line(line)
        if result is None:
            logger.debug("Line not parsed, storing whole message")
            result = {'message': line, '@version': 1}
        else:
            logger.debug("Match: %s", str(result))
            result['message'] = line
            result['@version'] = 1
        if '@timestamp' not in result:
            result['@timestamp'] = datetime.utcnow().replace(tzinfo=pytz.utc).isoformat()
        yield self.indexer.index(result)


    @gen.coroutine
    def on_close(self):
        #Close es connection?
        logger.info("Connection to %s closed", self.address)
        yield []

class MockIndexer:
    def index(self, doc):
        pass

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
        if self.es_config is None:
            indexer = MockIndexer()
        else:
            indexer = ESIndexer(**self.es_config)
        cn = ConnectionHandler(stream, address,
                               ESIndexer(**self.es_config),
                               self._load_processor())
        yield cn.on_connect()
