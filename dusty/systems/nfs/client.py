from __future__ import absolute_import

import logging
from subprocess import CalledProcessError
import time

from ... import constants
from ..virtualbox import get_host_ip
from ...log import log_to_client
from ...subprocess import call_demoted, check_call_demoted, check_output_demoted, check_output_demoted
from ...compiler.spec_assembler import get_all_repos

def mount_active_repos():
    remount_repos(get_all_repos(active_only=True, include_specs_repo=False))

def remount_repos(repos):
    _start_nfs_client()
    for i, repo in enumerate(repos):
        _unmount_repo(repo)
        _mount_repo(repo, wait_for_server=(i==0))

def unmount_all_repos():
    mounts = check_output_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME,
                                   'mount | {{ grep {} || true; }}'.format(constants.VM_REPOS_DIR)])
    mounted_dirs = []
    for mount in mounts.splitlines():
        for word in mount.split(' '):
            if constants.VM_REPOS_DIR in word:
                mounted_dirs.append(word)
    for mounted_dir in mounted_dirs:
        _unmount_vm_dir(mounted_dir)

def _start_nfs_client():
    check_call_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME,
                        'sudo /usr/local/etc/init.d/nfs-client start'])

def _unmount_repo(repo):
    _unmount_vm_dir(repo.vm_path)

def _unmount_vm_dir(vm_dir):
    call_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME,
                  'sudo umount -l {}'.format(vm_dir)])

def _mount_repo(repo, wait_for_server=False):
    """
    This function will create the VM directory where a repo will be mounted, if it
    doesn't exist.  If wait_for_server is set, it will wait up to 10 seconds for
    the nfs server to start, by retrying mounts that fail with 'Connection Refused'.

    If wait_for_server is not set, it will attempt to run the mount command once
    """
    check_call_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME,
                        'sudo mkdir -p {}'.format(repo.vm_path)])
    if wait_for_server:
        for i in range(0,10):
            try:
                _run_mount_command(repo)
                return
            except CalledProcessError as e:
                if 'Connection refused' in e.output:
                    logging.info('Failed to mount repo; waiting for nfsd to restart')
                    time.sleep(1)
                else:
                    logging.info(e.output)
                    raise e
        log_to_client('Failed to mount repo {}'.format(repo.short_name))
        raise RuntimeError('Unable to mount repo with NFS')
    else:
        _run_mount_command(repo)

def _run_mount_command(repo):
    # Check output is used here so that if it raises an error, the output can be parsed
    return check_output_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME,
                                 'sudo mount {}'.format(_nfs_mount_args_string(repo))], redirect_stderr=True)

def _nfs_mount_args_string(repo):
    mount_string = '-t nfs {} '.format(_nfs_options_string())
    mount_string += '{}:{} '.format(get_host_ip(), repo.local_path)
    mount_string += repo.vm_path
    return mount_string

def _nfs_options_string():
    return '-o async,udp,noatime'
