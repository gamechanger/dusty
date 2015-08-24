import sys
import logging
import logging.handlers
from .constants import SOCKET_PATH, SOCKET_LOGGER_NAME
from threading import RLock

handler = None
log_to_client_lock = RLock()

class DustySocketHandler(logging.Handler):
    def __init__(self, connection_socket):
        super(DustySocketHandler, self).__init__()
        self.connection_socket = connection_socket

    def emit(self, record):
        msg = self.format(record)
        self.connection_socket.sendall("{}\n".format(msg.encode('utf-8').strip()))

class DustyClientTestingSocketHandler(logging.Handler):
    def __init__(self):
        super(DustyClientTestingSocketHandler, self).__init__()
        self.log_to_client_output = ''

    def emit(self, record):
        msg = self.format(record)
        self.log_to_client_output += '{}\n'.format(msg.encode('utf-8').strip())

client_logger = logging.getLogger(SOCKET_LOGGER_NAME)

def configure_logging():
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s:%(name)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.captureWarnings(True)

def make_socket_logger(connection_socket):
    global handler
    logger = logging.getLogger(SOCKET_LOGGER_NAME)
    handler = DustySocketHandler(connection_socket)
    logger.addHandler(handler)

def log_to_client(message):
    with log_to_client_lock:
        client_logger.info(message)

def close_socket_logger():
    global handler
    logger = logging.getLogger(SOCKET_LOGGER_NAME)
    logger.removeHandler(handler)
    handler = None

def configure_client_logging():
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO,
                        format='%(message)s')
