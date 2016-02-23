import sys
import os

import tornado.ioloop
import yaml

from . import MainHandler, ConnectionHandler

DEFAULT_PORT = 8899
DEFAULT_ADDRESS = '0.0.0.0'

def run():
    config_path = os.path.abspath(sys.argv[1])
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)

    if 'parse_spec' in config:
        class FromConfigHandler(ConnectionHandler):
            SPEC = config['parse_spec']
        server = MainHandler(
            connection_class=FromConfigHandler,
            es_host=config.get('es_host', 'localhost'),
            es_port=9200
        )
    port = config.get('port', DEFAULT_PORT)
    server.listen(port, address=DEFAULT_ADDRESS)
    tornado.ioloop.IOLoop.current().start()
