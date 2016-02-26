import sys
import os
import logging.config

import tornado.ioloop
import yaml

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'default': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}},
    'handlers': {'default': {'class': 'logging.StreamHandler',
                             'formatter': 'default',
                             'stream': 'ext://sys.stdout',
                             'level': 0}},
    'root': {'handlers': ['default'], 'level': 0},
}

def run():
    config_path = os.path.abspath(sys.argv[1])
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file)
    logging.config.dictConfig(config.pop('logging', DEFAULT_LOGGING))
    from . import App
    try:
        app = App(config)
        app.run()
    except:
        logging.exception('Exception: ')
        raise
