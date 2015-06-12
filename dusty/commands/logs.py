from ..systems.docker import get_dusty_containers
from . import utils

def tail_container_logs(app_or_service_name, follow=False, lines=None):
    container = get_dusty_containers([app_or_service_name], include_exited=True)[0]
    args = ['logs']
    if follow:
        args.append('-f')
    if lines:
        args.append('--tail={}'.format(lines))
    args.append(container['Id'])
    utils.exec_docker(*args)
