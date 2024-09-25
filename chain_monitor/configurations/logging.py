import logging.config
import sys

logging_config = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout
        }
    },
    'loggers': {
        'chain_monitor': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}


def setup_logging(force_logging_stdout=True):
    if force_logging_stdout:
        for handler_name, handler_config in list(logging_config['handlers'].items()):
            if handler_config['class'] != 'logging.StreamHandler':
                logging_config['handlers'][handler_name] = {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'stream': sys.stdout
                }
    logging.config.dictConfig(logging_config)
