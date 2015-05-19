import os
import logging
import subprocess
from copy import copy

import yaml

from ... import constants
from ...config import get_config_value, assert_config_key
from .demote import demote_to_user

def _check_demoted(fn, shell_args, env=None):
    if env:
        passed_env = copy(os.environ)
        passed_env.update(env)
    else:
        passed_env = None
    return fn(shell_args, preexec_fn=demote_to_user(get_config_value('docker_user')), env=passed_env)

def _check_call_demoted(shell_args, env=None):
    return _check_demoted(subprocess.check_call, shell_args, env)

def _check_output_demoted(shell_args, env=None):
    return _check_demoted(subprocess.check_output, shell_args, env)

def _get_docker_env():
    output = _check_output_demoted(['boot2docker', 'shellinit'])
    env = {}
    for line in output.splitlines():
        k, v = line.strip().split()[1].split('=')
        env[k] = v
    return env

def _ensure_docker_vm_is_online():
    """Start the boot2docker VM if it is not already running."""
    logging.info('Initializing boot2docker, this will take a while the first time it runs')
    _check_call_demoted(['boot2docker', 'init'])
    logging.info('Making sure the boot2docker VM is started')
    _check_call_demoted(['boot2docker', 'start'])

def _composefile_path():
    return os.path.join(constants.COMPOSE_DIR, 'docker-compose.yml')

def _write_composefile(compose_config):
    if not os.path.exists(constants.COMPOSE_DIR):
        os.makedirs(constants.COMPOSE_DIR)
    with open(_composefile_path(), 'w') as f:
        f.write(yaml.dump(compose_config, default_flow_style=False))

def _compose_up():
    _check_call_demoted(['docker-compose', '-f', _composefile_path(), '-p', 'dusty', 'up', '-d', '--allow-insecure-ssl'],
                        env=_get_docker_env())

def update_running_containers_from_spec(compose_config):
    """Takes in a Compose spec from the Dusty Compose compiler,
    writes it to the Compose spec folder so Compose can pick it
    up, then does everything needed to make sure boot2docker is
    up and running containers with the updated config."""
    assert_config_key('docker_user')
    _write_composefile(compose_config)
    _ensure_docker_vm_is_online()
    _compose_up()
