import os
import logging
from subprocess import check_call

from ... import constants
from ...config import get_config_value, assert_config_key
from ...demote import check_call_demoted
from ...source import local_repo_path, vm_repo_path, repo_is_overridden
from ...log import log_to_client
from dusty.compiler.spec_assembler import get_repo_of_app_or_library, get_assembled_specs

def _ensure_remote_dir_exists(remote_dir):
    check_call_demoted(['boot2docker', 'ssh', 'sudo mkdir -p {0}; sudo chown -R docker {0}'.format(remote_dir)])

def _sync_dir(local_dir, remote_dir):
    _ensure_remote_dir_exists(remote_dir)
    ssh_opts = 'ssh -p 2022 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i /Users/{}/.ssh/id_boot2docker'.format(get_config_value('mac_username'))
    command = ['rsync', '-e', ssh_opts, '-az', '--exclude', '*/.git', '--delete', '--force',
               '{}/'.format(local_dir), 'docker@localhost:{}'.format(remote_dir)]
    logging.debug('Executing rsync command: {}'.format(' '.join(command)))
    check_call(command)

def sync_repos(repos):
    logging.info('Syncing repos over rsync')
    assert_config_key('mac_username')
    for repo_name in repos:
        repo_type = 'overridden' if repo_is_overridden(repo_name) else 'Dusty-managed'
        remote_path = vm_repo_path(repo_name)
        log_to_client('Syncing {} repo {} to remote at {}'.format(repo_type, repo_name, remote_path))
        _sync_dir(local_repo_path(repo_name), remote_path)

def sync_repos_by_app_name(app_names):
    repos = set()
    assembled_specs = get_assembled_specs()
    for app_name in app_names:
        for lib_name in assembled_specs['apps'][app_name]['depends']['libs']:
            repos.add(get_repo_of_app_or_library(lib_name))
        repos.add(get_repo_of_app_or_library(app_name))
    sync_repos(repos)
