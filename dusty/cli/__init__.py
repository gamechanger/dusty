"""Dusty: Docker development environments

Usage:
  dusty [options] [<command>] [<args>...]

Commands:
  bundles    Manage which sets of applications to run
  config     Get or set Dusty config variables
  disk       Manage and inspect the boot2docker VM's disk usage
  dump       Print diagnostic information for bug reports
  logs       Tail logs for a Dusty-managed service
  repos      Manage Git repos used for running Dusty applications
  restart    Restart Dusty-managed containers
  script     Execute predefined scripts inside running containers
  shell      Open a shell inside a running container
  stop       Stop Dusty-managed containers
  sync       Sync files from the local OS to the boot2docker VM
  up         Set up the Dusty environment and start activated applications

For help on a specific command, provide the '-h' flag to the command, e.g. 'dusty repos -h'
"""

import sys
import socket

from docopt import docopt

from ..constants import SOCKET_PATH, SOCKET_TERMINATOR, SOCKET_ERROR_TERMINATOR
from ..payload import Payload
from . import bundles, config, dump, disk, logs, repos, restart, script, shell, stop, sync, up

MODULE_MAP = {
    'bundles': bundles,
    'config': config,
    'disk': disk,
    'dump': dump,
    'logs': logs,
    'repos': repos,
    'restart': restart,
    'script': script,
    'shell': shell,
    'stop': stop,
    'sync': sync,
    'up': up
}

def _run_command(sock, command):
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

def _connect_to_daemon():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(.2)
    try:
        sock.connect(SOCKET_PATH)
    except:
        print 'Couldn\'t connect to dusty\'s socket; make sure the daemon is running, and that it\'s not connected to another client'
        sys.exit(1)
    sock.settimeout(None)
    return sock

def main():
    args = docopt(__doc__, options_first=True)
    command, command_args = args['<command>'], args['<args>']
    if command is None:
        print __doc__.strip()
        sys.exit(0)
    if command not in MODULE_MAP:
        print "No such command {}.".format(command)
        print "\n{}".format(__doc__.strip())
        sys.exit(1)

    result = MODULE_MAP[command].main(command_args)
    if isinstance(result, Payload):
        sock = _connect_to_daemon()
        try:
            errored = _run_command(sock, result.serialize())
        except KeyboardInterrupt:
            print "Dusty Client stopping on KeyboardInterrupt..."
            print "-----Dusty Daemon is still processing your last command!-----"
        sys.exit(1 if errored else 0)
