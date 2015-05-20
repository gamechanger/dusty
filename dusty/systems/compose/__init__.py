import os
import logging
import subprocess
from copy import copy
import re

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

def _dusty_shared_folder_already_exists():
    """Return boolean indicating whether the dusty shared folder
    has already been created in the boot2docker VM."""
    output = _check_output_demoted(['VBoxManage', 'showvminfo', 'boot2docker-vm', '--machinereadable'])
    return re.compile('^SharedFolderName.*dusty', re.MULTILINE).search(output) is not None

def _ensure_dusty_shared_folder_exists():
    """Create the dusty shared folder in the boot2docker VM if it does
    not already exist. Creating shared folders requires the VM to
    be powered down."""
    if not _dusty_shared_folder_already_exists():
        logging.info('Stopping boot2docker VM to allow creation of shared volume')
        _check_call_demoted(['boot2docker', 'stop'])
        logging.info('Creating dusty shared folder inside boot2docker VM')
        _check_call_demoted(['VBoxManage', 'sharedfolder', 'add', 'boot2docker-vm',
                             '--name', 'dusty', '--hostpath', constants.CONFIG_DIR])

def _ensure_dusty_shared_folder_is_mounted():
    logging.info('Mounting dusty shared folder (if it is not already mounted)')
    mount_cmd = 'sudo mkdir {0}; sudo mount -t vboxsf -o uid=1000,gid=50 dusty {0}'.format(constants.CONFIG_DIR)
    mount_if_cmd = 'if [ ! -d "{}" ]; then {}; fi'.format(constants.CONFIG_DIR, mount_cmd)
    _check_call_demoted(['boot2docker', 'ssh', mount_if_cmd])

def _get_docker_env():
    output = _check_output_demoted(['boot2docker', 'shellinit'])
    env = {}
    for line in output.splitlines():
        k, v = line.strip().split()[1].split('=')
        env[k] = v
    return env

def _ensure_docker_vm_exists():
    """Initialize the boot2docker VM if it does not already exist."""
    logging.info('Initializing boot2docker, this will take a while the first time it runs')
    _check_call_demoted(['boot2docker', 'init'])

def _ensure_docker_vm_is_online():
    """Start the boot2docker VM if it is not already running."""
    logging.info('Making sure the boot2docker VM is started')
    _check_call_demoted(['boot2docker', 'start'])

def _composefile_path():
    return os.path.join(constants.COMPOSE_DIR, 'docker-compose.yml')

def _write_composefile(compose_config):
    logging.info('Writing new Composefile')
    if not os.path.exists(constants.COMPOSE_DIR):
        os.makedirs(constants.COMPOSE_DIR)
    with open(_composefile_path(), 'w') as f:
        f.write(yaml.dump(compose_config, default_flow_style=False))

def _compose_up():
    logging.info('Running docker-compose up')
    _check_call_demoted(['docker-compose', '-f', _composefile_path(), '-p', 'dusty', 'up', '-d', '--allow-insecure-ssl'],
                        env=_get_docker_env())

def update_running_containers_from_spec(compose_config):
    """Takes in a Compose spec from the Dusty Compose compiler,
    writes it to the Compose spec folder so Compose can pick it
    up, then does everything needed to make sure boot2docker is
    up and running containers with the updated config."""
    assert_config_key('docker_user')
    _write_composefile(compose_config)
    _ensure_docker_vm_exists()
    _ensure_dusty_shared_folder_exists()
    _ensure_docker_vm_is_online()
    _ensure_dusty_shared_folder_is_mounted()
    _compose_up()
