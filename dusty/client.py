"""A dead-simple client for talking to Dusty over its Unix socket."""

import sys
import socket

from .constants import SOCKET_PATH, SOCKET_TERMINATOR

def run_command(sock, command):
    error_response = False
    sock.sendall(command)
    while True:
        data = sock.recv(65535)
        if data:
            sys.stdout.write(data.decode('utf-8'))
            if data.startswith('ERROR: '):
                error_response = True
            if data.endswith(SOCKET_TERMINATOR):
                break
        else:
            break

    return error_response

def main():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCKET_PATH)
    if len(sys.argv) == 1:
        print 'TODO: Show client help message if no args provided'
        return

    errored = run_command(sock, ' '.join(sys.argv[1:]))
    sys.exit(1 if errored else 0)

if __name__ == '__main__':
    main()
