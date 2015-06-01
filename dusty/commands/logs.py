import os

from ..systems.docker import get_dusty_containers
from .utils import exec_docker

def tail_container_logs(app_or_service_name):
    container = get_dusty_containers([app_or_service_name])[0]
    exec_docker('logs', '-f', container['Id'])
