import os

from prettytable import PrettyTable

from ..compiler.spec_assembler import get_specs, get_assembled_specs
from ..systems.virtualbox import asset_is_set, asset_value, asset_vm_path, remove_asset
from ..systems.rsync import sync_local_path_to_vm
from ..log import log_to_client

def list_by_app_or_lib(app_or_lib):
    spec = get_specs().get_app_or_lib(app_or_lib)
    table = PrettyTable(["Asset", "Is Set", "Required", "In-Container Path"])
    for asset in spec['assets']:
        table.add_row([asset['name'], 'X' if asset_is_set(asset['name']) else '', 'X' if asset['required'] else '', asset['path']])
    log_to_client(table.get_string())

def _get_string_of_set(items):
    return ', '.join(sorted(items))

def list_all():
    table = PrettyTable(["Asset", "Is Set", "Used By", "Required By"])
    assembled_specs = get_assembled_specs()
    for asset_name, asset_info in assembled_specs['assets'].iteritems():
        used_by_display = _get_string_of_set(asset_info['used_by'])
        required_by_display = _get_string_of_set(asset_info['required_by'])
        table.add_row([asset_name, 'X' if asset_is_set(asset_name) else '', used_by_display, required_by_display])
    log_to_client(table.get_string())

def read_asset(asset_key):
    if not asset_is_set(asset_key):
        log_to_client('Asset {} isn\'t set'.format(asset_key))
        return
    log_to_client(asset_value(asset_key))

def set_asset(asset_key, local_path):
    sync_local_path_to_vm(local_path, asset_vm_path(asset_key))

def unset_asset(asset_key):
    if not asset_is_set(asset_key):
        log_to_client('Asset {} isn\'t set'.format(asset_key))
        return
    remove_asset(asset_key)
