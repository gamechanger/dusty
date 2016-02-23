from ..log import log_to_client
from ..payload import daemon_command
from ..systems.virtualbox import (shut_down_docker_vm, delete_docker_vm_host_only_interface,
                                  ensure_docker_vm_is_started, regenerate_docker_vm_certificates)

@daemon_command
def run_doctor():
    log_to_client('Shutting down Dusty VM to perform remedial operations')
    shut_down_docker_vm()
    delete_docker_vm_host_only_interface()
    ensure_docker_vm_is_started()
    regenerate_docker_vm_certificates()
    # TODO: Remove this step once initialize_docker_vm is smarter
    # The problem is we couldn't do our standard initialization
    # steps (making our symlinks, installing rsync, etc) since
    # the network was having problems. We need to shut the VM
    # down so the next dusty up attempts to do these. Instead
    # of basing init off VM state, we should write a file somewhere
    # and base the operation off of that.
    log_to_client('Doctor operations successful')
    log_to_client('Shutting down VM so next dusty up initializes properly')
    shut_down_docker_vm()
    log_to_client('Run dusty up to bring up the VM')
