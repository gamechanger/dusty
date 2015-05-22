import logging
from ..compiler import (compose as compose_compiler, nginx as nginx_compiler,
                        port_spec as port_spec_compiler, spec_assembler)
from ..systems import compose, hosts, nginx, virtualbox, rsync
from ..constants import SOCKET_LOGGER_NAME

def start_local_env():
    """ This command will use the compilers to get compose specs
    will pass those specs to the systems that need them. Those
    systems will in turn launch the services needed to make the
    local environment go"""
    active_repos = spec_assembler.get_all_repos(active_only=True, include_specs_repo=False)
    logger = logging.getLogger(SOCKET_LOGGER_NAME)
    logger.info("Compiling together the assembled specs\n")
    assembled_spec = spec_assembler.get_assembled_specs()
    logger.info("Compiling the port specs\n")
    port_spec = port_spec_compiler.get_port_spec_document(assembled_spec)
    logger.info("Compiling the nginx config\n")
    nginx_config = nginx_compiler.get_nginx_configuration_spec(port_spec)
    logger.info("Compiling docker-compose config\n")
    compose_config = compose_compiler.get_compose_dict(assembled_spec, port_spec)

    logger.info("Saving port forwarding to hosts file\n")
    hosts.update_hosts_file_from_port_spec(port_spec)
    logger.info("Ensuring virtualbox vm is running\n")
    virtualbox.initialize_docker_vm()
    logger.info("Saving port to virtualbox vm\n")
    virtualbox.update_virtualbox_port_forwarding_from_port_spec(port_spec)
    rsync.sync_repos(active_repos)
    logger.info("Saving nginx config and ensure nginx is running\n")
    nginx.update_nginx_from_config(nginx_config)
    logger.info("Saving docker-compose config and starting all containers\n")
    compose.update_running_containers_from_spec(compose_config)

    yield "Your local environment is now started"

def stop_local_env():
    """Stop any currently running Docker containers associated with
    Dusty. Does not remove the containers."""
    yield "Stopping all running containers associated with Dusty"
    compose.stop_running_containers()
    yield "Dusty containers are stopped"
