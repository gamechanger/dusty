from copy import copy
import os
import subprocess

from ..systems.docker import get_docker_env


def _executable_path(executable_name):
    return subprocess.check_output(['which', executable_name]).strip()


def exec_docker(*args):
    updated_env = copy(os.environ)
    updated_env.update(get_docker_env())
    args = args + (updated_env,)
    os.execle(_executable_path('docker'), 'docker', *args)
