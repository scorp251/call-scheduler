import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from app.config import config

log = logging.getLogger(__name__)
log.setLevel(config['general']['loglevel'])
log.propagate = False

LOG_FORMAT = '[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s [%(pathname)s at %(lineno)d]'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S %z'
formatter = logging.Formatter(LOG_FORMAT, TIMESTAMP_FORMAT)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logfile = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../../' + config['general']['logfile'])

file_handler = RotatingFileHandler(logfile, 'a', 10 * 1024 * 1024, 10)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

if config['general']['logconsole'] == 'True':
    log.addHandler(stream_handler)
