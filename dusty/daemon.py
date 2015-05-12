import os
import atexit
import logging
import socket

from .preflight import preflight_check
from .log import configure_logging
from .notifier import notify
from .constants import SOCKET_PATH

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
    logging.info('Listening on socket at {}'.format(SOCKET_PATH))

    notify('Dusty is listening for commands')
    atexit.register(notify, 'Dusty daemon has terminated')

    while True:
        connection, client_address = sock.accept()
        try:
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                logging.info('Received command: {}'.format(data))
        finally:
            connection.close()

def main():
    notify('Dusty initializing...')
    configure_logging()
    preflight_check()
    _listen_on_socket()

if __name__ == '__main__':
    main()
