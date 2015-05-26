from .client import call_command_from_client
from ..systems.compose import get_dusty_containers
from ..demote import thread_output_client_only

def tail_container_logs(service_name):
    container = get_dusty_containers([service_name])[0]
    call_command_from_client(['boot2docker', 'ssh', 'docker', 'logs', container['Id']])

def stream_container_logs(service_name):
    container = get_dusty_containers([service_name])[0]
    call_command_from_client(['boot2docker', 'ssh', 'docker', 'logs', '-f', container['Id']])

