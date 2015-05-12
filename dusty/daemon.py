import os
import atexit
import logging
import socket

from .preflight import preflight_check
from .log import configure_logging
from .notifier import notify
from .constants import SOCKET_PATH, SOCKET_TERMINATOR

def _clean_up_existing_socket(socket_path):
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

def _listen_on_socket(socket_path):
    _clean_up_existing_socket(socket_path)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(socket_path)
    sock.listen(1)
    logging.info('Listening on socket at {}'.format(socket_path))

    notify('Dusty is listening for commands')
    atexit.register(notify, 'Dusty daemon has terminated')

    while True:
        try:
            connection, client_address = sock.accept()
            try:
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    logging.info('Received command: {}'.format(data))
                    connection.sendall('Received: {}\n'.format(data))
                    connection.sendall(SOCKET_TERMINATOR)
            finally:
                connection.close()
        except KeyboardInterrupt:
            break
        except:
            logging.exception('Exception on socket listen')

def main():
    notify('Dusty initializing...')
    configure_logging()
    preflight_check()
    _listen_on_socket(SOCKET_PATH)

if __name__ == '__main__':
    main()
