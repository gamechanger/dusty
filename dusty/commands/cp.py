import os
import uuid
import tempfile
from contextlib import contextmanager
import shutil

from .. import constants
from ..path import vm_cp_path
from ..systems.rsync import sync_local_path_to_vm, sync_local_path_from_vm, vm_path_is_directory
from ..systems.compose import (move_dir_inside_container, move_file_inside_container,
                               copy_path_inside_container)

@contextmanager
def _cleanup_path(path):
    try:
        yield
    finally:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

def copy_between_containers(source_name, source_path, dest_name, dest_path):
    temp_path = os.path.join(tempfile.mkdtemp(), str(uuid.uuid1()))
    with _cleanup_path(temp_path):
        copy_to_local(temp_path, source_name, source_path, demote=False)
        copy_from_local(temp_path, dest_name, dest_path, demote=False)

def copy_from_local(local_path, remote_name, remote_path, demote=True):
    temp_identifier = str(uuid.uuid1())
    if os.path.isdir(local_path):
        sync_local_path_to_vm(local_path, os.path.join(vm_cp_path(remote_name), temp_identifier), demote=demote)
        move_dir_inside_container(remote_name, os.path.join(constants.CONTAINER_CP_DIR, temp_identifier), remote_path)
    else:
        sync_local_path_to_vm(local_path, os.path.join(vm_cp_path(remote_name), temp_identifier), demote=demote)
        move_file_inside_container(remote_name, os.path.join(constants.CONTAINER_CP_DIR, temp_identifier), remote_path)

def copy_to_local(local_path, remote_name, remote_path, demote=True):
    temp_identifier = str(uuid.uuid1())
    copy_path_inside_container(remote_name, remote_path, os.path.join(constants.CONTAINER_CP_DIR, temp_identifier))
    vm_path = os.path.join(vm_cp_path(remote_name), temp_identifier)
    is_dir = vm_path_is_directory(vm_path)
    sync_local_path_from_vm(local_path, vm_path, demote=demote, is_dir=is_dir)
