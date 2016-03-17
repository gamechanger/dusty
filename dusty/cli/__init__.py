"""Dusty: Docker-powered development environments

Usage:
  dusty [options] [<command>] [<args>...]

Commands:
  assets     Manage files that don't live in version control
  bundles    Manage which sets of applications to run
  config     Get or set Dusty config variables
  cp         Copy files between local filesystem and containers
  disk       Manage and inspect the Dusty VM's disk usage
  doctor     Attempt to fix networking issues with your Dusty VM
  dump       Print diagnostic information for bug reports
  env        Set environment variable overrides in containers
  logs       Tail logs for a Dusty-managed service
  repos      Manage Git repos used for running Dusty applications
  restart    Restart Dusty-managed containers
  scripts    Execute predefined scripts inside running containers
  setup      Configure Dusty after installation
  shell      Open a shell inside a running container
  shutdown   Shut down the Dusty VM
  status     Show info on activated apps, services and libs
  stop       Stop Dusty-managed containers
  test       Run test scripts in isolated environments
  up         Set up the Dusty environment and start activated applications
  upgrade    Upgrade Dusty to a new version
  validate   Validates that Dusty specs have correct fields and references
  version    Print Dusty daemon's current version

Options:
  -d    Run the Dusty daemon
  -v    Print the installed dusty version

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
from . import (assets, bundles, config, cp, dump, disk, doctor, env, logs, repos, restart,
               scripts, shell, shutdown, stop, up, upgrade, validate, version, setup, test, status)
from .. import constants

MODULE_MAP = {
    'assets': assets,
    'bundles': bundles,
    'config': config,
    'cp': cp,
    'disk': disk,
    'doctor': doctor,
    'dump': dump,
    'env': env,
    'logs': logs,
    'repos': repos,
    'restart': restart,
    'scripts': scripts,
    'setup': setup,
    'shell': shell,
    'shutdown': shutdown,
    'status': status,
    'stop': stop,
    'test': test,
    'up': up,
    'upgrade': upgrade,
    'validate': validate,
    'version': version,
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
            stripped = data.replace(constants.SOCKET_ACK, '').replace(constants.SOCKET_TERMINATOR, '').replace(constants.SOCKET_ERROR_TERMINATOR, '')
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
        try:
            errored = _run_command(sock, payload.serialize())
        except KeyboardInterrupt:
            print "Dusty Client stopping on KeyboardInterrupt..."
            print "-----Dusty Daemon is still processing your last command!-----"
            return 0
        return errored
    else:
        payload.run()

def main():
    # Dispatch to daemon's docopt immediately so
    # we can process daemon-specific options
    if '-d' in sys.argv:
        return run_daemon()

    args = docopt(__doc__, options_first=True)
    if args['-v']:
        print 'Dusty version {}'.format(constants.VERSION)
        sys.exit(0)
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
        sys.exit(0)
