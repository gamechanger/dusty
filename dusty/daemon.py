import os
import atexit
import logging
import socket

from .preflight import preflight_check
from .log import configure_logging, make_socket_logger, close_socket_logger
from .notifier import notify
from .constants import SOCKET_PATH, SOCKET_TERMINATOR, SOCKET_ERROR_TERMINATOR
from .commands import process_command

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
    os.chmod(socket_path, 0777) # don't delete the 0, it makes Python interpret this as octal
    sock.listen(1)
    logging.info('Listening on socket at {}'.format(socket_path))

    notify('Dusty is listening for commands')
    atexit.register(notify, 'Dusty daemon has terminated')

    while True:
        try:
            connection, client_address = sock.accept()
            make_socket_logger(connection)
            try:
                while True:
                    data = connection.recv(1024)
                    if not data:
                        break
                    logging.info('Received command: {}'.format(data))
                    try:
                        for line in process_command(data):
                            encoded_line = line
                            if isinstance(encoded_line, basestring):
                                encoded_line = line.encode('utf-8')
                            connection.sendall('{}\n'.format(encoded_line))
                    except Exception as e:
                        logging.exception("Daemon encountered exception while processing command")
                        connection.sendall('ERROR: {}\n'.format(e.message).encode('utf-8'))
                        connection.sendall(SOCKET_ERROR_TERMINATOR)
                    else:
                        connection.sendall(SOCKET_TERMINATOR)
            finally:
                close_socket_logger()
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
