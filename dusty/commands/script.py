import textwrap
from prettytable import PrettyTable

from ..log import log_to_client
from ..compiler.spec_assembler import get_specs
from . import utils
from ..systems.docker import get_dusty_container_name

def script_info_for_app(app_name):
    app_specs = get_specs()['apps'].get(app_name)
    if not app_specs:
        raise KeyError('No app found named {} in specs'.format(app_name))
    if not app_specs['scripts']:
        log_to_client('No scripts registered for app {}'.format(app_name))
        return

    table = PrettyTable(['Script', 'Description'])
    for script_spec in app_specs['scripts']:
        table.add_row([script_spec['name'],
                       '\n'.join(textwrap.wrap(script_spec['description'], 80))])
    log_to_client(table.get_string(sortby='Script'))

def execute_script(app_name, script_name, script_arguments=[]):
    app_specs = get_specs()['apps'].get(app_name)
    if not app_specs:
        raise KeyError('No app found named {} in specs'.format(app_name))
    script_spec = None
    for script_dict in app_specs['scripts']:
        if script_dict['name'] == script_name:
            script_spec = script_dict
    if script_spec is None:
        raise KeyError('No script found named {} in specs for app {}'.format(script_name, app_name))

    base_script_command = '; '.join(script_spec['command'])
    if script_arguments == []:
        script_string = base_script_command
    else:
        script_string = '{} {}'.format(base_script_command, ' '.join(script_arguments))

    container_name = get_dusty_container_name(app_name)
    utils.exec_docker('exec', '-ti', container_name, 'sh', '-c', script_string)
