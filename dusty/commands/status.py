from prettytable import PrettyTable

from ..compiler.spec_assembler import get_assembled_specs
from ..log import log_to_client
from ..systems.docker import get_dusty_containers

def _has_activate_container(spec_type, service_name):
    if spec_type == 'libs':
        return False
    return get_dusty_containers([service_name]) != []

def get_dusty_status():
    assembled_specs = get_assembled_specs()
    table = PrettyTable(["Name", "Type", "Has Active Container"])
    for spec_type in ['apps', 'libs', 'services']:
        for service_name, spec in assembled_specs[spec_type].iteritems():
            has_activate_container = _has_activate_container(spec_type, service_name)
            table.add_row([service_name, spec_type, 'X' if has_activate_container else ''])
    log_to_client(table.get_string(sortby="Type"))
