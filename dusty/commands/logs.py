import logging

from ..systems.docker import get_dusty_containers
from . import utils

def tail_container_logs(app_or_service_name, follow=False, lines=None, timestamps=False):
    containers = get_dusty_containers([app_or_service_name], include_exited=True)
    if len(containers) == 0:
        logging.info('No container exists which corresponds to {}'.format(app_or_service_name))
        return
    container = containers[0]
    args = ['logs']
    if follow:
        args.append('-f')
    if timestamps:
        args.append('-t')
    if lines:
        args.append('--tail={}'.format(lines))
    args.append(container['Id'])
    utils.exec_docker(*args)
