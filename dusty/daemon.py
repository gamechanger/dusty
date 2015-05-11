import os
import sys
import logging
import socket

from .preflight import preflight_check
from .notifier import notify

SOCKET_PATH = '/var/run/dusty/dusty.sock'

def _configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.captureWarnings(True)

def _clean_up_existing_socket():
    try:
        os.unlink(SOCKET_PATH)
    except OSError:
        if os.path.exists(SOCKET_PATH):
            raise

def _listen_on_socket():
    _clean_up_existing_socket()

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    sock.listen(1)

    notify('Dusty is listening for commands')

    while True:
        connection, client_address = sock.accept()
        try:
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                print data
        finally:
            connection.close()

def main():
    notify('Dusty initializing...')
    _configure_logging()
    preflight_check()
    _listen_on_socket()

if __name__ == '__main__':
    main()
