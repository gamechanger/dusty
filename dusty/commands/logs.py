import os

from ..systems.compose import get_dusty_containers
from .utils import _executable_path

def tail_container_logs(app_or_service_name):
    container = get_dusty_containers([app_or_service_name])[0]
    os.execl(_executable_path('docker'), 'docker', 'logs', '-f', container['Id'])
