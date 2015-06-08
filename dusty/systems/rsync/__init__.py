import os
import logging
from subprocess import check_call, CalledProcessError

from ... import constants
from ...config import get_config_value
from ...subprocess import check_call_demoted, check_and_log_output_and_error_demoted
from ...source import Repo
from ...path import parent_dir
from ...log import log_to_client
from dusty.compiler.spec_assembler import get_repo_of_app_or_library, get_assembled_specs

def _ensure_vm_dir_exists(remote_dir):
    check_call_demoted(['boot2docker', 'ssh', 'sudo mkdir -p {0}; sudo chown -R docker {0}'.format(remote_dir)])

def _rsync_command(local_path, remote_path, is_dir=True, from_local=True, exclude_git=True):
    ssh_opts = 'ssh -p 2022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i /Users/{}/.ssh/id_boot2docker'.format(get_config_value(constants.CONFIG_MAC_USERNAME_KEY))
    command = ['rsync', '-e', ssh_opts, '-az', '--force']
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

# For the sync_repos_by_... functions to work, they really need to take already expanded specs
def _sync_repos_by_type_name(expanded_specs, type_names, dusty_type):
    repos = set()
    for type_name in type_names:
        for lib_name in expanded_specs[dusty_type][type_name].get('depends', {}).get('libs', []):
            repos.add(get_repo_of_app_or_library(lib_name))
        repos.add(get_repo_of_app_or_library(type_name))
    sync_repos(repos)

def sync_repos_by_app_name(expanded_specs, app_names):
    _sync_repos_by_type_name(expanded_specs, app_names, 'apps')

def sync_repos_by_lib_name(expanded_specs, lib_names):
    _sync_repos_by_type_name(expanded_specs, lib_names, 'libs')

