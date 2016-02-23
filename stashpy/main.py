import sys
import os
import logging

import tornado.ioloop
import yaml

from . import MainHandler, ConnectionHandler

DEFAULT_PORT = 8899
DEFAULT_ADDRESS = '0.0.0.0'

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


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
