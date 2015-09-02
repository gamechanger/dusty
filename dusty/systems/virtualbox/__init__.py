from __future__ import absolute_import

import os
import re
import logging
import textwrap
import time
from subprocess import CalledProcessError

from ... import constants
from ...memoize import memoized
from ...config import get_config_value
from ...subprocess import check_and_log_output_and_error_demoted, check_output_demoted, check_call_demoted, call_demoted
from ...log import log_to_client

def _command_for_vm(command_list):
    ssh_command = ['docker-machine', 'ssh', constants.VM_MACHINE_NAME]
    ssh_command.extend([command_list])
    return ssh_command

def _run_command_on_vm(command_list):
    return check_and_log_output_and_error_demoted(_command_for_vm(command_list))

def _check_output_on_vm(command_list):
    return check_output_demoted(_command_for_vm(command_list))

def _ensure_rsync_is_installed():
    logging.info('Installing rsync inside the Docker VM')
    # We're running tce-load twice as a hack to get around the fact that, for
    # completely unknown reasons, tce-load will return with an exit code of 1 after
    # initial install even if it works just fine. Subsequent install attempts will
    # be no-ops with a return code of 0.
    _run_command_on_vm('which rsync || tce-load -wi rsync || tce-load -wi rsync')

def _ensure_persist_dir_is_linked():
    logging.info('Linking {} to VBox disk (if it is not already linked)'.format(constants.VM_PERSIST_DIR))
    mkdir_if_cmd = 'if [ ! -d /mnt/sda1{0} ]; then sudo mkdir /mnt/sda1{0}; fi'.format(constants.VM_PERSIST_DIR)
    mount_if_cmd = 'if [ ! -d {0} ]; then sudo ln -s /mnt/sda1{0} {0}; fi'.format(constants.VM_PERSIST_DIR)
    _run_command_on_vm(mkdir_if_cmd)
    _run_command_on_vm(mount_if_cmd)

def _ensure_vm_dir_exists(vm_dir):
    logging.info('Creating {} in VM to support dusty'.format(vm_dir))
    mkdir_if_cmd = 'if [ ! -d {0} ]; then sudo mkdir {0}; fi'.format(vm_dir)
    _run_command_on_vm(mkdir_if_cmd)

def _ensure_cp_dir_exists():
    _ensure_vm_dir_exists(constants.VM_CP_DIR)

def _ensure_assets_dir_exists():
    _ensure_vm_dir_exists(constants.VM_ASSETS_DIR)

def _dusty_vm_exists():
    existing_vms = check_output_demoted(['docker-machine', 'ls', '-q'])
    for line in existing_vms.splitlines():
        if line == constants.VM_MACHINE_NAME:
            return True
    return False

def _init_docker_vm():
    """Initialize the Dusty VM if it does not already exist."""
    if not _dusty_vm_exists():
        logging.info('Initializing new Dusty VM with Docker Machine')
        machine_options = ['--driver', 'virtualbox',
                           '--virtualbox-cpu-count', '-1',
                           '--virtualbox-memory', str(get_config_value(constants.CONFIG_VM_MEM_SIZE))]
        check_call_demoted(['docker-machine', 'create'] + machine_options + [constants.VM_MACHINE_NAME],
                           redirect_stderr=True)

def _start_docker_vm():
    """Start the Dusty VM if it is not already running."""
    logging.info('Making sure the Dusty VM is started')
    check_call_demoted(['docker-machine', 'start', constants.VM_MACHINE_NAME], redirect_stderr=True)

def _stop_docker_vm():
    """Stop the Dusty VM if it is not already stopped."""
    logging.info('Stopping the Dusty VM')
    check_call_demoted(['docker-machine', 'stop', constants.VM_MACHINE_NAME], redirect_stderr=True)

def _get_vm_config():
    return check_output_demoted(['VBoxManage', 'showvminfo', '--machinereadable', constants.VM_MACHINE_NAME]).splitlines()

def docker_vm_is_running():
    return check_output_demoted(['docker-machine', 'status', constants.VM_MACHINE_NAME]).strip().lower() == 'running'

def ensure_docker_vm_is_started():
    _init_docker_vm()
    _start_docker_vm()

def initialize_docker_vm():
    ensure_docker_vm_is_started()
    _ensure_rsync_is_installed()
    _ensure_persist_dir_is_linked()
    _ensure_cp_dir_exists()
    _ensure_assets_dir_exists()

@memoized
def get_docker_vm_ip():
    return check_output_demoted(['docker-machine', 'ip', constants.VM_MACHINE_NAME]).rstrip()

def _parse_df_output(df_line):
    split_line = df_line.split()
    return {'total': split_line[1],
            'used': split_line[2],
            'free': split_line[3],
            'usage_pct': split_line[4]}

def _format_df_dict(df_dict):
    formatted_usage = "Usage: {}\n".format(df_dict['usage_pct'])
    formatted_usage += "Total Size: {}\n".format(df_dict['total'])
    formatted_usage += "Used: {}\n".format(df_dict['used'])
    formatted_usage += "Free: {}".format(df_dict['free'])
    return formatted_usage

def get_docker_vm_disk_info(as_dict=False):
    df_output = check_output_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME,
                                      'df -h /mnt/sda1 | grep /dev/sda1'])
    df_line = df_output.split('\n')[0]
    df_dict = _parse_df_output(df_line)
    return df_dict if as_dict else _format_df_dict(df_dict)

def get_vm_hostonly_adapter():
    config_lines = _get_vm_config()
    for line in config_lines:
        if line.startswith('hostonlyadapter'):
            return line.split('=')[1].strip('"').rstrip('"')

def _get_hostonly_config():
    return check_output_demoted(['VBoxManage', 'list', 'hostonlyifs']).splitlines()

@memoized
def get_host_ip():
    adapter = get_vm_hostonly_adapter()
    host_only_config = _get_hostonly_config()

    in_adapter_block = False
    for line in host_only_config:
        if line.startswith('Name'):
            if adapter in line:
                in_adapter_block = True
            else:
                in_adapter_block = False
        if in_adapter_block:
            if line.startswith('IPAddress'):
                return line.split()[1]
    raise RuntimeError('Host IP in host only network not found')

def required_absent_assets(assembled_specs):
    required_and_absent = []
    for asset_key, asset_info in assembled_specs['assets'].iteritems():
        if asset_info['required_by'] and not asset_is_set(asset_key):
            required_and_absent.append(asset_key)
    return required_and_absent

@memoized
def get_assets_on_vm():
    dir_contents = _check_output_on_vm('ls {}'.format(constants.VM_ASSETS_DIR))
    return set(dir_contents.splitlines())

def asset_vm_path(asset_key):
    return os.path.join(constants.VM_ASSETS_DIR, asset_key)

def asset_is_set(asset_key):
    return asset_key in get_assets_on_vm()

def asset_value(asset_key):
    return _check_output_on_vm('sudo cat {}'.format(asset_vm_path(asset_key)))

def remove_asset(asset_key):
    _run_command_on_vm('sudo rm -f {}'.format(asset_vm_path(asset_key)))
