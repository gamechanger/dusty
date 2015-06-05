from ..systems.docker import get_dusty_containers
from .utils import exec_docker

def tail_container_logs(app_or_service_name, lines=None):
    container = get_dusty_containers([app_or_service_name])[0]
    if lines is None:
        exec_docker('logs', '-f', container['Id'])
    else:
        exec_docker('logs', '-f', '--tail={}'.format(lines), container['Id'])
