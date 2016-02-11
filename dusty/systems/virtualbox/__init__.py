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
    ssh_command = ['ssh', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null',
                   '-i', _vm_key_path(), 'docker@{}'.format(get_docker_vm_ip())]
    ssh_command.extend([command_list])
    return ssh_command

@memoized
def _vm_key_path():
    dusty_user = get_config_value(constants.CONFIG_MAC_USERNAME_KEY)
    return os.path.expanduser('~{}/.docker/machine/machines/{}/id_rsa'.format(dusty_user,
                                                                              constants.VM_MACHINE_NAME))

def run_command_on_vm(command_list, quiet_on_success=True):
    return check_and_log_output_and_error_demoted(_command_for_vm(command_list),
                                                  quiet_on_success=quiet_on_success)

def check_output_on_vm(command_list, redirect_stderr=False):
    return check_output_demoted(_command_for_vm(command_list), redirect_stderr=redirect_stderr)

def check_call_on_vm(command_list, redirect_stderr=False):
    return check_call_demoted(_command_for_vm(command_list), redirect_stderr=redirect_stderr)

def call_on_vm(command_list, redirect_stderr=False):
    return call_demoted(_command_for_vm(command_list), redirect_stderr=redirect_stderr)

def _ensure_rsync_is_installed():
    # We're running tce-load twice as a hack to get around the fact that, for
    # completely unknown reasons, tce-load will return with an exit code of 1 after
    # initial install even if it works just fine. Subsequent install attempts will
    # be no-ops with a return code of 0.
    run_command_on_vm('which rsync || tce-load -wi rsync || tce-load -wi rsync')

def _ensure_persist_dir_is_linked():
    mkdir_if_cmd = 'if [ ! -d /mnt/sda1{0} ]; then sudo mkdir /mnt/sda1{0}; fi'.format(constants.VM_PERSIST_DIR)
    mount_if_cmd = 'if [ ! -d {0} ]; then sudo ln -s /mnt/sda1{0} {0}; fi'.format(constants.VM_PERSIST_DIR)
    run_command_on_vm(mkdir_if_cmd)
    run_command_on_vm(mount_if_cmd)

def _ensure_vm_dir_exists(vm_dir):
    mkdir_if_cmd = 'if [ ! -d {0} ]; then sudo mkdir {0}; fi'.format(vm_dir)
    run_command_on_vm(mkdir_if_cmd)

def _ensure_cp_dir_exists():
    _ensure_vm_dir_exists(constants.VM_CP_DIR)

def _ensure_assets_dir_exists():
    _ensure_vm_dir_exists(constants.VM_ASSETS_DIR)

def _dusty_vm_exists():
    """We use VBox directly instead of Docker Machine because it
    shaves about 0.5 seconds off the runtime of this check."""
    existing_vms = check_output_demoted(['VBoxManage', 'list', 'vms'])
    for line in existing_vms.splitlines():
        if '"{}"'.format(constants.VM_MACHINE_NAME) in line:
            return True
    return False

def _apply_nat_dns_host_resolver():
    """
    This will make the Dusty VM always use the host's DNS resolver for lookups.
    It solves an issue we were seeing where the VM's resolving settings would get
    out of date when a laptop was moved between routers with different settings,
    resulting in DNS lookup failures on the VM.
    """
    check_and_log_output_and_error_demoted(
        ['VBoxManage', 'modifyvm', constants.VM_MACHINE_NAME, '--natdnshostresolver1', 'on'],
        quiet_on_success=True)

def _apply_nat_net_less_greedy_subnet():
    """By default, VirtualBox claims 10.0.2.x for itself as part of its NAT routing
    scheme. This subnet is commonly used on internal networks, making this a pretty
    damn greedy choice. We instead alter the VM to use the less greedy subnet of
    10.174.249.x which is less likely to conflict."""
    check_and_log_output_and_error_demoted(
        ['VBoxManage', 'modifyvm', constants.VM_MACHINE_NAME, '--natnet1', '10.174.249/24'],
        quiet_on_success=True)

def _init_docker_vm():
    """Initialize the Dusty VM if it does not already exist."""
    if not _dusty_vm_exists():
        logging.info('Initializing new Dusty VM with Docker Machine')
        machine_options = ['--driver', 'virtualbox',
                           '--virtualbox-cpu-count', '-1',
                           '--virtualbox-memory', str(get_config_value(constants.CONFIG_VM_MEM_SIZE)),
                           '--virtualbox-hostonly-nictype', constants.VM_NIC_TYPE]
        check_call_demoted(['docker-machine', 'create'] + machine_options + [constants.VM_MACHINE_NAME],
                           redirect_stderr=True)

def _start_docker_vm():
    """Start the Dusty VM if it is not already running."""
    is_running = docker_vm_is_running()
    if not is_running:
        log_to_client('Starting docker-machine VM {}'.format(constants.VM_MACHINE_NAME))
        _apply_nat_dns_host_resolver()
        _apply_nat_net_less_greedy_subnet()
        check_and_log_output_and_error_demoted(['docker-machine', 'start', constants.VM_MACHINE_NAME], quiet_on_success=True)
    return is_running

def _stop_docker_vm():
    """Stop the Dusty VM if it is not already stopped."""
    check_call_demoted(['docker-machine', 'stop', constants.VM_MACHINE_NAME], redirect_stderr=True)

def _get_vm_config():
    return check_output_demoted(['VBoxManage', 'showvminfo', '--machinereadable', constants.VM_MACHINE_NAME]).splitlines()

def docker_vm_is_running():
    """Using VBoxManage is 0.5 seconds or so faster than Machine."""
    running_vms = check_output_demoted(['VBoxManage', 'list', 'runningvms'])
    for line in running_vms.splitlines():
        if '"{}"'.format(constants.VM_MACHINE_NAME) in line:
            return True
    return False

def _vm_not_using_pcnet_fast_iii():
    for line in _get_vm_config():
        if 'nictype1' in line and constants.VM_NIC_TYPE not in line:
            return True
    return False

def _apply_nic_fix():
    """Set NIC 1 to use PCnet-FAST III. The host-only NIC type is
    set during docker-machine create (and Machine will change it
    back if it is changed manually), which is why we only change
    NIC 1 here."""
    log_to_client('Setting NIC 1 to use PCnet-FAST III')
    check_call_demoted(['VBoxManage', 'modifyvm', constants.VM_MACHINE_NAME, '--nictype1', constants.VM_NIC_TYPE])

def ensure_docker_vm_is_started():
    _init_docker_vm()
    # Switch VM to use PCnet-FAST III which we have observed to
    # have much better performance than the default.
    if _vm_not_using_pcnet_fast_iii():
        log_to_client('Stopping Dusty VM to apply NIC fix for faster networking performance')
        if docker_vm_is_running():
            _stop_docker_vm()
        _apply_nic_fix()
    was_already_running = _start_docker_vm()
    return was_already_running

def initialize_docker_vm():
    was_already_running = ensure_docker_vm_is_started()
    # These operations are somewhat expensive, so we only
    # run them if there's a chance we are bringing up a
    # fresh VM or temporary filesystems may need to be
    # reinitialized following a restart.
    if not was_already_running:
        _ensure_rsync_is_installed()
        _ensure_persist_dir_is_linked()
        _ensure_cp_dir_exists()
        _ensure_assets_dir_exists()

@memoized
def get_docker_vm_ip():
    ssh_port = None
    for line in _get_vm_config():
        # Something in the VM chain, either VirtualBox or Machine, helpfully
        # sets up localhost-to-VM forwarding on port 22. We can inspect this
        # rule to determine the port on localhost which gets forwarded to
        # 22 in the VM.
        if line.startswith('Forwarding'):
            spec = line.split('=')[1].strip('"')
            name, protocol, host, host_port, target, target_port = spec.split(',')
            if name == 'ssh' and protocol == 'tcp' and target_port == '22':
                ssh_port = host_port
                break

    if ssh_port:
        # Now we can SSH to the VM on localhost:ssh_port. We do this to
        # get inside the VM and determine the VM's local address on
        # the virtualized network. This IP is what we're ultimately
        # trying to return from this function.
        ip_addr = check_output_demoted(['ssh', '-o', 'StrictHostKeyChecking=no',
                                        '-o', 'UserKnownHostsFile=/dev/null',
                                        '-i', _vm_key_path(), '-p', ssh_port,
                                        'docker@127.0.0.1', 'ip addr show dev eth1'])
        for line in ip_addr.splitlines():
            line = line.strip()
            if line.startswith('inet') and not line.startswith('inet6'):
                ip = line.split(' ')[1].split('/')[0]
                return ip

    # If all our crazy hacks up there don't work, we can still get the IP
    # from Machine directly. The reason we don't do this normally is
    # because it's really slow, taking around 600ms on my fast machine.
    logging.warning('Could not get IP the fast way, falling back to Docker Machine')
    return check_output_demoted(['docker-machine', 'ip', constants.VM_MACHINE_NAME]).rstrip()

@memoized
def get_docker_bridge_ip():
    logging.info('Attempting to get the docker bridge IP')
    for _ in range(5):
        result = check_output_on_vm("ip route | grep docker0 | awk '{print $NF}'").rstrip()
        if result:
            return result
        time.sleep(1)
        logging.info('Retrying...')

    raise ValueError('Could not get Docker bridge IP from Virtualbox, VM may not be fully initialized')

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
    df_output = check_output_on_vm('df -h /mnt/sda1 | grep /dev/sda1')
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
    dir_contents = check_output_on_vm('ls {}'.format(constants.VM_ASSETS_DIR))
    return set(dir_contents.splitlines())

def asset_vm_path(asset_key):
    return os.path.join(constants.VM_ASSETS_DIR, asset_key)

def asset_is_set(asset_key):
    return asset_key in get_assets_on_vm()

def asset_value(asset_key):
    return check_output_on_vm('sudo cat {}'.format(asset_vm_path(asset_key)))

def remove_asset(asset_key):
    run_command_on_vm('sudo rm -f {}'.format(asset_vm_path(asset_key)))
