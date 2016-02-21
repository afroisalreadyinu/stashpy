import sys
import os

import tornado.ioloop
import yaml

from . import MainHandler, ConnectionHandler

DEFAULT_PORT = 8899

def run():
    config_path = os.path.abspath(sys.argv[1])
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)

    if 'parse_spec' in config:
        class FromConfigHandler(ConnectionHandler):
            SPEC = config['parse_spec']
        server = MainHandler(connection_class=FromConfigHandler)
    port = config.get('port', DEFAULT_PORT)
    server.listen(port)
    tornado.ioloop.IOLoop.current().start()
