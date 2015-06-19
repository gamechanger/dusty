from prettytable import PrettyTable

from ..compiler.spec_assembler import get_assembled_specs
from ..log import log_to_client
from ..systems.docker import get_dusty_containers

def _has_active_container(spec_type, service_name):
    if spec_type == 'lib':
        return False
    return get_dusty_containers([service_name]) != []

def get_dusty_status():
    assembled_specs = get_assembled_specs()
    table = PrettyTable(["Name", "Type", "Has Active Container"])
    import logging
    logging.error(assembled_specs._document)
    for spec in assembled_specs.get_apps_libs_and_services():
        spec_type = spec.type_singular
        service_name = spec.name
        has_activate_container = _has_active_container(spec_type, service_name)
        table.add_row([service_name, spec_type, 'X' if has_activate_container else ''])
    log_to_client(table.get_string(sortby="Type"))
