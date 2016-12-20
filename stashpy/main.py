import sys
import os
import logging
import logging.config

import tornado.ioloop
import yaml

from .handler import MainHandler
from stashpy import constants

logger = logging.getLogger(__name__)

class App:
    def __init__(self, config):
        assert 'processor_spec' in config or 'processor_class' in config
        self.config = config
        self.main = MainHandler(config)

    def run(self):
        port = self.config.get('port', constants.DEFAULT_PORT)
        self.main.listen(port, address=constants.DEFAULT_ADDRESS)
        logger.info("Stashpy started, accepting connections on {}:{}".format(
            'localhost',
            port))
        io_loop = tornado.ioloop.IOLoop.current()
        if not io_loop._running:
            io_loop.start()

def run():
    config_path = os.path.abspath(sys.argv[1])
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)
    logging.config.dictConfig(config.pop('logging', constants.DEFAULT_LOGGING))
    try:
        app = App(config)
        app.run()
    except:
        logging.exception('Exception: ')
        raise
