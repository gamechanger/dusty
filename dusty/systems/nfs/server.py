from __future__ import absolute_import

import logging
import os
from subprocess import CalledProcessError

from ... import constants
from .. import config_file
from ...compiler.spec_assembler import get_all_repos
from ...log import log_to_client
from ...source import Repo
from ..virtualbox import get_docker_vm_ip
from ...subprocess import check_and_log_output_and_error, check_output, check_call

def configure_nfs_server():
    """
    This function is used with `dusty up`.  It will check all active repos to see if
    they are exported.  If any are missing, it will replace current dusty exports with
    exports that are needed for currently active repos, and restart
    the nfs server
    """
    vm_ip = get_docker_vm_ip()
    repos_for_export = get_all_repos(active_only=True, include_specs_repo=False)

    current_exports = _get_current_exports()
    needed_exports = _get_exports_for_repos(repos_for_export, vm_ip)

    _ensure_managed_repos_dir_exists()

    if not needed_exports.difference(current_exports):
        if not _server_is_running():
            _restart_server()
        return

    _write_exports_config(needed_exports)
    _restart_server()

def add_exports_for_repos(repos):
    """
    This function will add needed entries to /etc/exports.  It will not remove any
    entries from the file.  It will then restart the server if necessary
    """
    vm_ip = get_docker_vm_ip()
    current_exports = _get_current_exports()
    needed_exports = _get_exports_for_repos(repos, vm_ip)

    if not needed_exports.difference(current_exports):
        if not _server_is_running():
            _restart_server()
        return

    _write_exports_config(current_exports.union(needed_exports))
    _restart_server()

def _ensure_managed_repos_dir_exists():
    """
    Our exports file will be invalid if this folder doesn't exist, and the NFS server
    will not run correctly.
    """
    if not os.path.exists(constants.REPOS_DIR):
        os.makedirs(constants.REPOS_DIR)

def _get_exports_for_repos(repos, vm_ip):
    config_set = set([_export_for_dusty_managed(vm_ip)])
    for repo in repos:
        if not repo.is_overridden:
            continue
        config_set.add(_export_for_repo(repo, vm_ip))
    return config_set

def _write_exports_config(exports_set):
    exports_config = ''.join(exports_set)
    current_config = _read_exports_contents()
    current_config = config_file.remove_current_dusty_config(current_config)
    current_config += config_file.create_config_section(exports_config)
    config_file.write(constants.EXPORTS_PATH, current_config)

def _export_for_dusty_managed(vm_ip):
    return '{} {} -alldirs -maproot=0:0\n'.format(os.path.realpath(constants.REPOS_DIR), vm_ip)

def _export_for_repo(repo, vm_ip):
    return '{} {} -alldirs -maproot={}\n'.format(os.path.realpath(repo.local_path), vm_ip, _maproot_for_repo(repo))

def _maproot_for_repo(repo):
    stat = os.stat(repo.local_path)
    return '{}:{}'.format(stat.st_uid, stat.st_gid)

def _check_exports():
    try:
        check_and_log_output_and_error(['nfsd', 'checkexports'], demote=False)
    except CalledProcessError:
        log_to_client('There\'s a conflict in your /etc/exports file - check existing configuration there and remove conflicts.')
        log_to_client('`nfsd checkexports` will verify that this file is valid.')
        raise

def _restart_server():
    _check_exports()
    if _server_is_running():
        check_call(['nfsd', 'update'], demote=False)
    else:
        log_to_client('Restarting NFS Server')
        check_and_log_output_and_error(['nfsd', 'restart'], demote=False)

def _read_exports_contents():
    if os.path.isfile(constants.EXPORTS_PATH):
        return config_file.read(constants.EXPORTS_PATH)
    else:
        return ''

def _get_current_exports():
    dusty_config = config_file.get_dusty_config_section(_read_exports_contents())
    return set(dusty_config.splitlines(True))

def _server_is_running():
    return 'nfsd is running' in check_output(['nfsd', 'status'])
