from copy import copy
import os
import subprocess
import sys
import pty

import psutil

from ..systems.docker import get_docker_env
from ..log import log_to_client, streaming_to_client
from ..subprocess import demote_to_user
from ..config import get_config_value
from .. import constants

def _executable_path(executable_name):
    return subprocess.check_output(['which', executable_name]).strip()

def exec_docker_options():
    exec_options = '-i'
    if sys.stdout.isatty():
        exec_options += 't'
    return exec_options

def exec_docker(*args):
    updated_env = copy(os.environ)
    updated_env.update(get_docker_env())
    args += (updated_env,)
    os.execle(_executable_path('docker'), 'docker', *args)

def pty_fork(*args):
    """Runs a subprocess with a PTY attached via fork and exec.
    The output from the PTY is streamed through log_to_client.
    This should not be necessary for most subprocesses, we
    built this to handle Compose up which only streams pull
    progress if it is attached to a TTY."""

    updated_env = copy(os.environ)
    updated_env.update(get_docker_env())
    args += (updated_env,)
    executable = args[0]
    demote_fn = demote_to_user(get_config_value(constants.CONFIG_MAC_USERNAME_KEY))

    child_pid, pty_fd = pty.fork()
    if child_pid == 0:
        demote_fn()
        os.execle(_executable_path(executable), *args)
    else:
        child_process = psutil.Process(child_pid)
        terminal = os.fdopen(pty_fd, 'r', 0)
        with streaming_to_client():
            while child_process.status() == 'running':
                output = terminal.read(1)
                log_to_client(output)
        _, exit_code = os.waitpid(child_pid, 0)
        if exit_code != 0:
            raise subprocess.CalledProcessError(exit_code, ' '.join(args[:-1]))
