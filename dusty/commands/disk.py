import logging

import docker

from ..log import log_to_client
from ..systems.compose import remove_exited_dusty_containers, remove_images
from ..systems.virtualbox import get_docker_vm_disk_info

def cleanup_inactive_containers():
    log_to_client("Cleaning up exited containers:")
    containers = remove_exited_dusty_containers()
    log_to_client("Done cleaning {} containers".format(len(containers)))

def cleanup_images():
    log_to_client("Cleaning up docker images without containers:")
    images = remove_images()
    log_to_client("Done removing {} images".format(len(images)))

def inspect_vm_disk():
    log_to_client("Boot2Docker VM Disk Usage:")
    log_to_client(get_docker_vm_disk_info())

