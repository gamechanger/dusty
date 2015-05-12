"""A dead-simple client for talking to Dusty over its Unix socket."""

import sys
import socket

from .constants import SOCKET_PATH, SOCKET_TERMINATOR

def run_command(sock, command):
    sock.sendall(command)
    while True:
        data = sock.recv(65535)
        if data:
            sys.stdout.write(data)
            if data.endswith(SOCKET_TERMINATOR):
                break
        else:
            break

def main():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCKET_PATH)
    if len(sys.argv) == 1:
        print 'TODO: Show client help message if no args provided'
    else:
        run_command(sock, ' '.join(sys.argv[1:]))
