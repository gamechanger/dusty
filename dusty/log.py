import sys
import logging
import logging.handlers
from .constants import SOCKET_PATH, SOCKET_LOGGER_NAME

logger = None

class DustySocketLogger(logging.getLoggerClass()):
    def __init__(self, socket_connection):
        self.socket_connection = socket_connection

    def log(self, level, msg, **kwargs):
        self._log("Dusty Logging:LV{}:{}\n".format(level, msg))

    def info(self, msg, **kwargs):
        self._log("Dusty Logging:INFO:{}\n".format(msg))

    def warning(self, msg, **kwargs):
        self._log("Dusty Logging:WARNING:{}\n".format(msg))

    def error(self, msg, **kwargs):
        self._log("Dusty Logging:ERROR:{}\n".format(msg))

    def critical(self, msg, **kwargs):
        self._log("Dusty Logging:CRITICAL:{}\n".format(msg))

    def exception(self, msg, **kwargs):
        self._log("Dusty Logging:EXCEPTION:{}\n".format(msg))

    def _log(self, msg):
        self.socket_connection.sendall(msg.encode('utf-8'))

def configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.captureWarnings(True)

def make_socket_logger(connection_socket):
    global logger
    logger = DustySocketLogger(connection_socket)

def get_socket_logger():
    return logger

