from ..compiler import (compose as compose_compiler, nginx as nginx_compiler,
                        port_spec as port_spec_compiler, spec_assembler)
from ..systems import compose, hosts, nginx, virtualbox, rsync

def start_local_env():
    """ This command will use the compilers to get compose specs
    will pass those specs to the systems that need them. Those
    systems will in turn launch the services needed to make the
    local environment go"""
    active_repos = spec_assembler.get_all_repos(active_only=True, include_specs_repo=False)
    assembled_spec = spec_assembler.get_assembled_specs()
    port_spec = port_spec_compiler.get_port_spec_document(assembled_spec)
    nginx_config = nginx_compiler.get_nginx_configuration_spec(port_spec)
    compose_config = compose_compiler.get_compose_dict(assembled_spec, port_spec)

    hosts.update_hosts_file_from_port_spec(port_spec)
    virtualbox.initialize_docker_vm()
    virtualbox.update_virtualbox_port_forwarding_from_port_spec(port_spec)
    rsync.sync_repos(active_repos)
    nginx.update_nginx_from_config(nginx_config)
    compose.update_running_containers_from_spec(compose_config)

    yield "Your local environment is now started"

def stop_local_env():
    """Stop any currently running Docker containers associated with
    Dusty. Does not remove the containers."""
    yield "Stopping all running containers associated with Dusty"
    compose.stop_running_containers()
    yield "Dusty containers are stopped"
