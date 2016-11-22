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

DEFAULT_PORT = 8899
DEFAULT_ADDRESS = '0.0.0.0'
