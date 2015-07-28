import logging

from prettytable import PrettyTable

from ..compiler.spec_assembler import get_assembled_specs
from ..log import log_to_client
from ..systems.docker import get_dusty_containers, get_docker_client
from ..payload import daemon_command

def _has_active_container(client, spec_type, service_name):
    if spec_type == 'lib':
        return False
    return get_dusty_containers([service_name], client=client) != []

@daemon_command
def get_dusty_status():
    client = get_docker_client()
    assembled_specs = get_assembled_specs()
    table = PrettyTable(["Name", "Type", "Has Active Container"])
    logging.error(assembled_specs._document)
    # Check for Dusty's special nginx container (used for host forwarding)
    table.add_row(['nginx', '', 'X' if get_dusty_containers(['nginx'], client=client) != [] else ''])
    for spec in assembled_specs.get_apps_libs_and_services():
        spec_type = spec.type_singular
        service_name = spec.name
        has_activate_container = _has_active_container(client, spec_type, service_name)
        table.add_row([service_name, spec_type, 'X' if has_activate_container else ''])
    log_to_client(table.get_string(sortby="Type"))
