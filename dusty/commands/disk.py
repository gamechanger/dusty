import docker
from ..systems.compose import remove_exited_dusty_containers, remove_unreferenced_images
from ..systems.virtualbox import get_docker_vm_disk_info

def cleanup_inactive_containers():
    yield "Cleaning up exited containers:"
    containers = remove_exited_dusty_containers()
    yield "Done cleaning {} containers".format(len(containers))

def cleanup_images():
    yield "Cleaning up docker images without containers:"
    images = remove_unreferenced_images()
    yield "Done removing {} images".format(len(images))

def inspect_vm_disk():
    yield "Boot2Docker VM Disk Usage:"
    yield get_docker_vm_disk_info()

