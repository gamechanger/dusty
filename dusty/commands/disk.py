import logging
import os
import time

import docker

from .. import constants
from ..log import log_to_client
from ..systems.docker.cleanup import remove_exited_dusty_containers, remove_images
from ..systems.virtualbox import get_docker_vm_disk_info, ensure_docker_vm_is_started
from ..systems.rsync import sync_local_path_to_vm, sync_local_path_from_vm

def cleanup_inactive_containers():
    log_to_client("Ensuring virtualbox VM is running")
    ensure_docker_vm_is_started()
    log_to_client("Cleaning up exited containers:")
    containers = remove_exited_dusty_containers()
    log_to_client("Done cleaning {} containers".format(len(containers)))

def cleanup_images():
    log_to_client("Ensuring virtualbox VM is running")
    ensure_docker_vm_is_started()
    log_to_client("Cleaning up docker images without containers:")
    images = remove_images()
    log_to_client("Done removing {} images".format(len(images)))

def inspect_vm_disk():
    log_to_client("Ensuring virtualbox VM is running")
    ensure_docker_vm_is_started()
    log_to_client("Boot2Docker VM Disk Usage:")
    log_to_client(get_docker_vm_disk_info())

def _backup_dir(destination_path):
    return os.path.join(destination_path, constants.LOCAL_BACKUP_DIR)

def _backup_dir_exists(destination_path):
    return os.path.exists(_backup_dir(destination_path))

def _ensure_backup_dir_exists(destination_path):
    if not _backup_dir_exists(destination_path):
        os.makedirs(_backup_dir(destination_path))

def _backup_modified_time(path):
    return time.ctime(os.path.getmtime(_backup_dir(path)))

def backup(destination_path):
    _ensure_backup_dir_exists(destination_path)
    log_to_client("Ensuring virtualbox VM is running")
    ensure_docker_vm_is_started()
    log_to_client("Syncing data from your VM to {}...".format(_backup_dir(destination_path)))
    sync_local_path_from_vm(os.path.join(destination_path, constants.LOCAL_BACKUP_DIR), constants.VM_PERSIST_DIR)

def restore(source_path):
    if not _backup_dir_exists(source_path):
        log_to_client("Can't find backup data to restore at {}".format(source_path))
        return
    log_to_client("Ensuring virtualbox VM is running")
    ensure_docker_vm_is_started()
    log_to_client("Restoring your backup last modified at {}".format(_backup_modified_time()))
    sync_local_path_to_vm(source_path, constants.VM_PERSIST_DIR)
