import sys
import os
import logging
import logging.config

import tornado.ioloop
import yaml

from .handler import MainHandler
from stashpy import constants

logger = logging.getLogger(__name__)


class TornadoApp:
    def __init__(self, config):
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


class RabbitApp:

    def __init__(self, config):
        self.config = config

    def run(self):
        pass

CONFIG_ERR_MSG = 'Either one of tcp_config or queue_config are allowed'

def read_config():
    config_path = os.path.abspath(sys.argv[1])
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)
    return config

def run():
    config = read_config()
    assert 'processor_spec' in config or 'processor_class' in config
    #so much code for an xor
    if 'tcp_config' in config:
        assert 'queue_config' not in config, CONFIG_ERR_MSG
    elif 'queue_config' in config:
        assert 'tcp_config' not in config, CONFIG_ERR_MSG
    else:
        assert False, CONFIG_ERR_MSG
    logging.config.dictConfig(config.pop('logging', constants.DEFAULT_LOGGING))
    try:
        app = TornadoApp(config) if 'tcp_config' in config else RabbitApp(config)
        app.run()
    except:
        logging.exception('Exception: ')
        raise
