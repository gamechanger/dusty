import sys
import logging
import logging.handlers
from .constants import SOCKET_PATH, SOCKET_LOGGER_NAME

handler = None

class DustySocketHandler(logging.Handler):
    def __init__(self, connection_socket):
        super(DustySocketHandler, self).__init__()
        self.connection_socket = connection_socket

    def emit(self, record):
        msg = self.format(record)
        self.connection_socket.sendall("{}\n".format(msg.encode('utf-8').strip()))


def configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.captureWarnings(True)

def make_socket_logger(connection_socket):
    global handler
    logger = logging.getLogger(SOCKET_LOGGER_NAME)
    handler = DustySocketHandler(connection_socket)
    logger.addHandler(handler)

def log_to_client(message):
    logger = logging.getLogger(SOCKET_LOGGER_NAME)
    logger.info(message)

def close_socket_logger():
    global handler
    logger = logging.getLogger(SOCKET_LOGGER_NAME)
    logger.removeHandler(handler)
    handler = None
