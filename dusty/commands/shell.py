from ..compiler.spec_assembler import get_specs
from .utils import exec_docker

def execute_shell(app_or_service_name):
    specs = get_specs()
    if app_or_service_name not in specs['apps'].keys() + specs['services'].keys():
        raise KeyError('No app or service found named {}'.format(app_or_service_name))
    exec_docker('exec', '-ti', 'dusty_{}_1'.format(app_or_service_name), '/bin/bash')
