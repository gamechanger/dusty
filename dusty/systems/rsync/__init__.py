import os
import logging
from subprocess import check_call, CalledProcessError

from ... import constants
from ...config import get_config_value
from ...subprocess import check_call_demoted, check_and_log_output_and_error_demoted
from ...source import Repo
from ...path import parent_dir
from ...log import log_to_client
from dusty.compiler.spec_assembler import get_same_container_repos_from_spec

def _ensure_vm_dir_exists(remote_dir):
    check_call_demoted(['boot2docker', 'ssh', 'sudo mkdir -p {0}; sudo chown -R docker {0}'.format(remote_dir)])

def _rsync_command(local_path, remote_path, is_dir=True, from_local=True, exclude_git=True):
    key_path = os.path.expanduser('~{}/.ssh/id_boot2docker'.format(get_config_value(constants.CONFIG_MAC_USERNAME_KEY)))
    ssh_opts = 'ssh -p 2022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {}'.format(key_path)
    command = ['rsync', '-e', ssh_opts, '-az', '--force', '--rsync-path', 'sudo rsync']
    if exclude_git:
        command += ['--exclude', '*/.git']
    if from_local:
        path_args = ['{}{}'.format(local_path, '/' if is_dir else ''), 'docker@localhost:{}'.format(remote_path)]
    else:
        path_args = ['docker@localhost:{}{}'.format(remote_path, '/' if is_dir else ''), local_path]
    command += path_args
    return command

def vm_path_is_directory(remote_path):
    """A weak check of whether a path in the boot2docker VM is a directory.
    This function returns False on any process error, so False may indicate
    other failures such as the path not actually existing."""
    try:
        check_call_demoted(['boot2docker', 'ssh', 'test -d {}'.format(remote_path)])
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

def sync_repos(repos):
    logging.info('Syncing repos over rsync')
    for repo in repos:
        repo_type = 'overridden' if repo.is_overridden else 'Dusty-managed'
        log_to_client('Syncing {} repo {} to remote at {}'.format(repo_type, repo.remote_path, repo.vm_path))
        sync_local_path_to_vm(repo.local_path, repo.vm_path)

def sync_repos_by_specs(specs_list):
    """
    Takes a list of app or lib specs (class DustySchema), and syncs the repos
    for those specs
    """
    repos = set()
    for spec in specs_list:
        repos = repos.union(get_same_container_repos_from_spec(spec))
    sync_repos(repos)
