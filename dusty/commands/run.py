import logging
from ..compiler import (compose as compose_compiler, nginx as nginx_compiler,
                        port_spec as port_spec_compiler, spec_assembler)
from ..systems import compose, hosts, nginx, virtualbox, rsync
from ..log import log_to_client

def start_local_env():
    """ This command will use the compilers to get compose specs
    will pass those specs to the systems that need them. Those
    systems will in turn launch the services needed to make the
    local environment go."""
    active_repos = spec_assembler.get_all_repos(active_only=True, include_specs_repo=False)
    log_to_client("Compiling together the assembled specs")
    assembled_spec = spec_assembler.get_assembled_specs()
    log_to_client("Compiling the port specs")
    port_spec = port_spec_compiler.get_port_spec_document(assembled_spec)
    log_to_client("Compiling the nginx config")
    nginx_config = nginx_compiler.get_nginx_configuration_spec(port_spec)
    log_to_client("Compiling docker-compose config")
    compose_config = compose_compiler.get_compose_dict(assembled_spec, port_spec)

    log_to_client("Saving port forwarding to hosts file")
    hosts.update_hosts_file_from_port_spec(port_spec)
    log_to_client("Ensuring virtualbox vm is running")
    virtualbox.initialize_docker_vm()
    log_to_client("Saving port to virtualbox vm")
    virtualbox.update_virtualbox_port_forwarding_from_port_spec(port_spec)
    log_to_client("Syncing local repos to the VM")
    rsync.sync_repos(active_repos)
    log_to_client("Saving nginx config and ensure nginx is running")
    nginx.update_nginx_from_config(nginx_config)
    log_to_client("Saving docker-compose config and starting all containers")
    compose.update_running_containers_from_spec(compose_config)

    yield "Your local environment is now started"

def stop_local_env(*services):
    """Stop any currently running Docker containers associated with
    Dusty. Does not remove the containers.

    Here, "services" refers to the Compose version of the term,
    so any existing running container, by name. This includes Dusty
    apps and services."""
    if services:
        yield "Stopping the following services: {}".format(', '.join(services))
    else:
        yield "Stopping all running containers associated with Dusty"
    compose.stop_running_containers(services)
