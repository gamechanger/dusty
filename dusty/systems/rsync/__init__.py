import os
import logging
from subprocess import check_call, CalledProcessError

from ... import constants
from ...config import get_config_value
from ...subprocess import check_call_demoted, check_and_log_output_and_error_demoted
from ...source import Repo
from ...path import parent_dir
from ...log import log_to_client
from ...compiler.spec_assembler import get_same_container_repos_from_spec
from ...systems.virtualbox import get_docker_vm_ip

def _ensure_vm_dir_exists(remote_dir):
    check_call_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME,
                        'sudo mkdir -p {0}; sudo chown -R docker {0}'.format(remote_dir)])

def _rsync_command(local_path, remote_path, is_dir=True, from_local=True, exclude_git=True):
    key_format_string = '~{}/.docker/machine/machines/{}/id_rsa'
    key_path = os.path.expanduser(key_format_string.format(get_config_value(constants.CONFIG_MAC_USERNAME_KEY),
                                                           constants.VM_MACHINE_NAME))
    ssh_opts = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {}'.format(key_path)
    command = ['rsync', '-e', ssh_opts, '-az', '--del', '--force', '--rsync-path', 'sudo rsync']
    if exclude_git:
        command += ['--exclude', '*/.git']
    if from_local:
        path_args = ['{}{}'.format(local_path, '/' if is_dir else ''), 'docker@{}:{}'.format(get_docker_vm_ip(), remote_path)]
    else:
        path_args = ['docker@{}:{}{}'.format(get_docker_vm_ip(), remote_path, '/' if is_dir else ''), local_path]
    command += path_args
    return command

def vm_path_is_directory(remote_path):
    """A weak check of whether a path in the Dusty VM is a directory.
    This function returns False on any process error, so False may indicate
    other failures such as the path not actually existing."""
    try:
        check_call_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME, 'test -d {}'.format(remote_path)])
    except CalledProcessError:
        return False
    return True

def sync_local_path_to_vm(local_path, remote_path, demote=False):
    is_dir = os.path.isdir(local_path)
    _ensure_vm_dir_exists(remote_path if is_dir else parent_dir(remote_path))
    command = _rsync_command(local_path, remote_path, is_dir=is_dir)
    logging.debug('Executing rsync command: {}'.format(' '.join(command)))
    check_call(command) if not demote else check_and_log_output_and_error_demoted(command)

def sync_local_path_from_vm(local_path, remote_path, demote=False, is_dir=True):
    command = _rsync_command(local_path, remote_path, is_dir=is_dir, from_local=False)
    logging.debug('Executing rsync command: {}'.format(' '.join(command)))
    check_call(command) if not demote else check_and_log_output_and_error_demoted(command)
