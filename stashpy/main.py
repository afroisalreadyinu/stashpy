import sys
import os

import tornado.ioloop
import yaml

from . import MainHandler, ConnectionHandler

def run():
    config_path = os.path.abspath(sys.argv[1])
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)

    if 'parse_spec' in config:
        class FromConfigHandler(ConnectionHandler):
            SPEC = config['parse_spec']
        server = MainHandler(connection_class=FromConfigHandler)
    server.listen(8888)
    tornado.ioloop.IOLoop.current().start()
