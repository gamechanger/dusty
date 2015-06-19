"""Dusty: Docker development environments

Usage:
  dusty [options] [<command>] [<args>...]

Commands:
  bundles    Manage which sets of applications to run
  config     Get or set Dusty config variables
  cp         Copy files between local filesystem and containers
  disk       Manage and inspect the boot2docker VM's disk usage
  dump       Print diagnostic information for bug reports
  logs       Tail logs for a Dusty-managed service
  repos      Manage Git repos used for running Dusty applications
  restart    Restart Dusty-managed containers
  scripts    Execute predefined scripts inside running containers
  setup      Configure Dusty after installation
  shell      Open a shell inside a running container
  status     Show info on activated apps, services and libs
  stop       Stop Dusty-managed containers
  sync       Sync repos from the local OS to the boot2docker VM
  test       Run test scripts in isolated environments
  up         Set up the Dusty environment and start activated applications
  validate   Validates that Dusty specs have correct fields and references

Options:
  -d    Run the Dusty daemon

For help on a specific command, provide the '-h' flag to the command, e.g. 'dusty repos -h'
"""

import logging
import os
import sys
import socket
import threading

from docopt import docopt

from ..daemon import main as run_daemon
from ..config import get_config_value
from ..log import configure_client_logging, log_to_client
from ..payload import Payload
from . import (bundles, config, cp, dump, disk, logs, repos, restart, script, shell, stop,
               sync, up, validate, setup, test, status)
from .. import constants

MODULE_MAP = {
    'bundles': bundles,
    'config': config,
    'cp': cp,
    'disk': disk,
    'dump': dump,
    'logs': logs,
    'repos': repos,
    'restart': restart,
    'scripts': script,
    'setup': setup,
    'shell': shell,
    'status': status,
    'stop': stop,
    'sync': sync,
    'test': test,
    'up': up,
    'validate': validate,
}

def _run_command(sock, command):
    error_response = False
    timer = threading.Timer(2, _notify_on_hang)
    timer.start()
    sock.sendall(command)
    while True:
        data = sock.recv(65535)
        timer.cancel()
        if data:
            stripped = data.decode('utf-8').replace(constants.SOCKET_TERMINATOR, '').replace(constants.SOCKET_ERROR_TERMINATOR, '')
            sys.stdout.write(stripped)
            if data.endswith(constants.SOCKET_TERMINATOR):
                break
            elif data.endswith(constants.SOCKET_ERROR_TERMINATOR):
                error_response = True
                break
        else:
            break

    return error_response

def _notify_on_hang():
    print 'The Dusty daemon will run your command once it\'s finished running previous commands'

def _connect_to_daemon():
    if not os.path.exists(constants.SOCKET_PATH):
        logging.info('Socket doesn\'t exist; make sure the Dusty daemon is running')
        return None
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(.2)
    try:
        sock.connect(constants.SOCKET_PATH)
    except:
        logging.info('Couldn\'t connect to Dusty\'s socket; make sure the daemon is running, and that it\'s not connected to another client')
        return None
    sock.settimeout(None)
    return sock

def _run_payload(payload):
    if payload.run_on_daemon:
        sock = _connect_to_daemon()
        if sock is None:
            return 1
        print 'The Dusty daemon will run your command once it\'s finished running previous commands'
        try:
            errored = _run_command(sock, payload.serialize())
        except KeyboardInterrupt:
            print "Dusty Client stopping on KeyboardInterrupt..."
            print "-----Dusty Daemon is still processing your last command!-----"
        return errored
    else:
        payload.run()

def main():
    # Dispatch to daemon's docopt immediately so
    # we can process daemon-specific options
    if '-d' in sys.argv:
        return run_daemon()

    args = docopt(__doc__, options_first=True)
    command, command_args = args['<command>'], args['<args>']
    if command is None:
        print __doc__.strip()
        sys.exit(0)
    if command not in MODULE_MAP:
        print "No such command {}.".format(command)
        print "\n{}".format(__doc__.strip())
        sys.exit(1)

    configure_client_logging()
    if command != 'validate' and command != 'setup':
      if not get_config_value(constants.CONFIG_SETUP_KEY):
          log_to_client('You must run `dusty setup` before you run any other commands')
          sys.exit(1)
    result = MODULE_MAP[command].main(command_args)
    if isinstance(result, Payload):
        errored = _run_payload(result)
        sys.exit(1 if errored else 0)
    elif isinstance(result, list):
        for payload in result:
            errored = _run_payload(payload)
            if errored:
                sys.exit(1)
