"""A dead-simple client for talking to Dusty over its Unix socket."""

import sys
import socket

from .constants import SOCKET_PATH, SOCKET_TERMINATOR, SOCKET_ERROR_TERMINATOR
from .commands import COMMAND_TREE

def run_command(sock, command):
    error_response = False
    sock.sendall(command)
    while True:
        data = sock.recv(65535)
        if data:
            sys.stdout.write(data.decode('utf-8'))
            if data.endswith(SOCKET_TERMINATOR):
                break
            elif data.endswith(SOCKET_ERROR_TERMINATOR):
                error_response = True
                break
        else:
            break

    return error_response

def main():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(.2)
    try:
        sock.connect(SOCKET_PATH)
    except:
        print 'Couldn\'t connect to dusty\'s socket; make sure the daemon is running!'
        sys.exit(1)
    sock.settimeout(None)
    if len(sys.argv) == 1:
        print 'Accepted commands: {}'.format(', '.join(sorted(COMMAND_TREE.keys())))
        return

    errored = run_command(sock, ' '.join(sys.argv[1:]))
    sys.exit(1 if errored else 0)
