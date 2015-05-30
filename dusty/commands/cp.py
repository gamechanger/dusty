import os
import uuid

from .. import constants
from ..systems.rsync import sync_local_dir_to_vm, sync_local_file_to_vm
from ..systems.compose import move_dir_inside_container, move_file_inside_container

def copy_between_containers(source_name, source_path, dest_name, dest_path):
    pass

def copy_from_local(local_path, remote_name, remote_path):
    temp_identifier = str(uuid.uuid1())
    if os.path.isdir(local_path):
        sync_local_dir_to_vm(local_path, os.path.join(constants.VM_CP_DIR, remote_name, temp_identifier), demote=True)
        move_dir_inside_container(remote_name, os.path.join(constants.CONTAINER_CP_DIR, temp_identifier), remote_path)
    else:
        sync_local_file_to_vm(local_path, os.path.join(constants.VM_CP_DIR, remote_name, temp_identifier), demote=True)
        move_file_inside_container(remote_name, os.path.join(constants.CONTAINER_CP_DIR, temp_identifier), remote_path)

def copy_to_local(local_path, remote_name, remote_path):
    pass
