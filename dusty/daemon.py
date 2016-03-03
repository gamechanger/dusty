"""Listen for user commands to Dusty

Usage:
  dusty -d [--suppress-warnings] [--preflight-only]

Options:
  --suppress-warnings  Do not display run time warnings to the client
  --preflight-only  Only run the preflight_check, then exit
"""

import os
import logging
import socket
import threading
# requests refused to play nicely with pyinstaller
import httplib

from docopt import docopt

from .preflight import preflight_check, refresh_preflight_warnings
from .log import configure_logging, make_socket_logger, close_socket_logger
from .constants import SOCKET_PATH, SOCKET_ACK, SOCKET_TERMINATOR, SOCKET_ERROR_TERMINATOR
from .payload import Payload, get_payload_function, init_yaml_constructor
from .memoize import reset_memoize_cache
from .warnings import daemon_warnings
from .config import refresh_config_warnings, check_and_load_ssh_auth
from . import constants, http_server

connection = None

def clean_up_socket():
    _clean_up_existing_socket(SOCKET_PATH)

def _clean_up_existing_socket(socket_path):
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise

def _send_warnings_to_client(connection, suppress_warnings):
    if daemon_warnings.has_warnings and not suppress_warnings:
        connection.sendall("{}\n".format(daemon_warnings.pretty()))

def _get_payload_function_data(payload):
    return get_payload_function(payload['fn_key']), payload['args'], payload['kwargs']

def _refresh_warnings():
    if daemon_warnings.has_warnings:
        refresh_config_warnings()
        refresh_preflight_warnings()

def _run_pre_command_functions(connection, suppress_warnings, client_version):
    check_and_load_ssh_auth()
    _refresh_warnings()

def close_client_connection(terminator=SOCKET_TERMINATOR):
    """This function allows downstream functions to close the connection with the client.
    This is necessary for the upgrade command, where execvp replaces the process before
    the main daemon loop can close the client connection"""
    try:
        connection.sendall(terminator)
    finally:
        close_socket_logger()
        connection.close()

def shut_down_http_server():
    logging.info('Daemon is shutting down HTTP server')
    try:
        h = httplib.HTTPConnection('{}:{}'.format(constants.DAEMON_HTTP_BIND_IP,
                                                  constants.DAEMON_HTTP_BIND_PORT))
        h.request('POST', '/shutdown')
        r = h.getresponse()
        if r.status != 200:
            raise ValueError('Got status code {} from response'.format(r.status))
    except Exception as e:
        logging.exception('Exception trying to shut down HTTP server')

def _start_http_server():
    """Start the daemon's HTTP server on a separate thread.
    This server is only used for servicing container status
    requests from Dusty's custom 502 page."""
    logging.info('Starting HTTP server at {}:{}'.format(constants.DAEMON_HTTP_BIND_IP,
                                                        constants.DAEMON_HTTP_BIND_PORT))
    thread = threading.Thread(target=http_server.app.run, args=(constants.DAEMON_HTTP_BIND_IP,
                                                                constants.DAEMON_HTTP_BIND_PORT))
    thread.daemon = True
    thread.start()

def _listen_on_socket(socket_path, suppress_warnings):
    global connection
    _clean_up_existing_socket(socket_path)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(socket_path)
    os.chmod(socket_path, 0777) # don't delete the 0, it makes Python interpret this as octal
    sock.listen(5)
    logging.info('Listening on socket at {}'.format(socket_path))

    while True:
        try:
            connection, client_address = sock.accept()
            connection.sendall(SOCKET_ACK)
            make_socket_logger(connection)
            try:
                data = connection.recv(1024)
                if not data:
                    continue
                payload = Payload.deserialize(data)
                client_version = payload['client_version']
                fn, args, kwargs = _get_payload_function_data(payload)
                suppress_warnings |= payload['suppress_warnings']
                logging.info('Received command. fn: {} args: {} kwargs: {}'.format(fn.__name__, args, kwargs))
                try:
                    if client_version != constants.VERSION:
                        raise RuntimeError("Dusty daemon is running version: {}, and client is running version: {}".format(constants.VERSION, client_version))
                    _run_pre_command_functions(connection, suppress_warnings, client_version)
                    _send_warnings_to_client(connection, suppress_warnings)
                    fn(*args, **kwargs)
                except Exception as e:
                    logging.exception("Daemon encountered exception while processing command")
                    error_msg = e.message if e.message else str(e)
                    _send_warnings_to_client(connection, suppress_warnings)
                    connection.sendall('ERROR: {}\n'.format(error_msg).encode('utf-8'))
                    close_client_connection(SOCKET_ERROR_TERMINATOR)
                else:
                    close_client_connection()
                finally:
                    reset_memoize_cache()
            except:
                close_client_connection()
        except KeyboardInterrupt:
            break
        except:
            logging.exception('Exception on socket listen')
    _clean_up_existing_socket(socket_path)

def main():
    args = docopt(__doc__)
    configure_logging()
    init_yaml_constructor()
    preflight_check()
    if args['--preflight-only']:
        return
    refresh_config_warnings()
    _start_http_server()
    _listen_on_socket(SOCKET_PATH, args['--suppress-warnings'])

if __name__ == '__main__':
    main()
