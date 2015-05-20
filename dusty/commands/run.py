
from ..compiler import compose, nginx, port_spec, spec_assembler
from ..systems import compose, hosts, nginx, virtualbox

def start_local_env():
    """ This command will use the compilers to get compose specs
    will pass those specs to the systems that need them. Those
    systems will in turn launch the services needed to make the
    local environment go"""
    assembled_spec = spec_assembler.get_assembled_specs()
    port_spec = port_spec.get_port_spec_document(assembled_spec)
    nginx_config = nginx.get_nginx_configuration_spec(port_spec)
    compose_config = compose.get_compose_dict(assembled_spec, port_spec)

    hosts.update_hosts_file_from_port_spec(port_spec)
    virtualbox.update_virtualbox_port_forwarding_from_port_spec(port_spec)
    nginx.update_nginx_from_config(nginx_config)
    compose.update_running_containers_from_spec(compose_config)
