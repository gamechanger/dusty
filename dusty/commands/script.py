import textwrap

from prettytable import PrettyTable

from ..log import log_to_client
from ..compiler.spec_assembler import get_specs
from .utils import exec_docker
from ..systems.compose import get_dusty_container_name

def script_info_for_app(app_name):
    app_specs = get_specs()['apps'].get(app_name)
    if not app_specs:
        raise KeyError('No app found named {} in specs'.format(app_name))
    if not app_specs.get('scripts'):
        log_to_client('No scripts registered for app {}'.format(app_name))
        return

    table = PrettyTable(['Script', 'Description'])
    for script_name, script_spec in app_specs['scripts'].iteritems():
        table.add_row([script_name,
                       '\n'.join(textwrap.wrap(script_spec.get('description', ''), 80))])
    log_to_client(table.get_string(sortby='Script'))

def execute_script(app_name, script_name):
    app_specs = get_specs()['apps'].get(app_name)
    if not app_specs:
        raise KeyError('No app found named {} in specs'.format(app_name))
    if 'scripts' not in app_specs or script_name not in app_specs['scripts']:
        raise KeyError('No script found named {} in specs for app {}'.format(script_name, app_name))

    container_name = get_dusty_container_name(app_name)
    exec_docker('exec', '-ti', container_name, 'sh', '-c', app_specs['scripts'][script_name]['command'])
