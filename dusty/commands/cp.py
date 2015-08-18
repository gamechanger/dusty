import os
import uuid
import tempfile
from contextlib import contextmanager
import shutil

from .. import constants
from ..log import log_to_client
from ..path import vm_cp_path
from ..systems.rsync import sync_local_path_to_vm, sync_local_path_from_vm, vm_path_is_directory
from ..systems.docker.files import (move_dir_inside_container, move_file_inside_container,
                               copy_path_inside_container, container_path_exists)
from ..payload import daemon_command

@contextmanager
def _cleanup_path(path):
    """Recursively delete a path upon exiting this context
    manager. Supports targets that are files or directories."""
    try:
        yield
    finally:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

@daemon_command
def copy_between_containers(source_name, source_path, dest_name, dest_path):
    """Copy a file from the source container to an intermediate staging
    area on the local filesystem, then from that staging area to the
    destination container.

    These moves take place without demotion for two reasons:
      1. There should be no permissions vulnerabilities with copying
         between containers because it is assumed the non-privileged
         user has full access to all Dusty containers.
      2. The temp dir created by mkdtemp is owned by the owner of the
         Dusty daemon process, so if we demoted our moves to/from that location
         they would encounter permission errors."""
    if not container_path_exists(source_name, source_path):
        raise RuntimeError('ERROR: Path {} does not exist inside container {}.'.format(source_path, source_name))
    temp_path = os.path.join(tempfile.mkdtemp(), str(uuid.uuid1()))
    with _cleanup_path(temp_path):
        copy_to_local(temp_path, source_name, source_path, demote=False)
        copy_from_local(temp_path, dest_name, dest_path, demote=False)

@daemon_command
def copy_from_local(local_path, remote_name, remote_path, demote=True):
    """Copy a path from the local filesystem to a path inside a Dusty
    container. The files on the local filesystem must be accessible
    by the user specified in mac_username."""
    if not os.path.exists(local_path):
        raise RuntimeError('ERROR: Path {} does not exist'.format(local_path))
    temp_identifier = str(uuid.uuid1())
    if os.path.isdir(local_path):
        sync_local_path_to_vm(local_path, os.path.join(vm_cp_path(remote_name), temp_identifier), demote=demote)
        move_dir_inside_container(remote_name, os.path.join(constants.CONTAINER_CP_DIR, temp_identifier), remote_path)
    else:
        sync_local_path_to_vm(local_path, os.path.join(vm_cp_path(remote_name), temp_identifier), demote=demote)
        move_file_inside_container(remote_name, os.path.join(constants.CONTAINER_CP_DIR, temp_identifier), remote_path)

@daemon_command
def copy_to_local(local_path, remote_name, remote_path, demote=True):
    """Copy a path from inside a Dusty container to a path on the
    local filesystem. The path on the local filesystem must be
    wrist-accessible by the user specified in mac_username."""
    if not container_path_exists(remote_name, remote_path):
        raise RuntimeError('ERROR: Path {} does not exist inside container {}.'.format(remote_path, remote_name))
    temp_identifier = str(uuid.uuid1())
    copy_path_inside_container(remote_name, remote_path, os.path.join(constants.CONTAINER_CP_DIR, temp_identifier))
    vm_path = os.path.join(vm_cp_path(remote_name), temp_identifier)
    is_dir = vm_path_is_directory(vm_path)
    sync_local_path_from_vm(local_path, vm_path, demote=demote, is_dir=is_dir)
