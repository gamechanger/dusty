from ..compiler.spec_assembler import get_specs
from . import utils
from ..systems.docker import get_dusty_container_name

def execute_shell(app_or_service_name):
    specs = get_specs()
    if app_or_service_name not in [spec.name for spec in specs.get_apps_and_services()]:
        raise KeyError('No app or service found named {}'.format(app_or_service_name))
    utils.exec_docker('exec', '-ti', get_dusty_container_name(app_or_service_name), '/bin/bash')
