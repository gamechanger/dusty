import os
import re
import logging

from ... import constants
from ...config import get_config_value
from ...subprocess import check_and_log_output_and_error_demoted, check_output_demoted
from ...log import log_to_client

def _ensure_rsync_is_installed():
    logging.info('Installing rsync inside the Docker VM')
    check_and_log_output_and_error_demoted(['boot2docker', 'ssh', 'tce-load -wi rsync'])

def _ensure_persist_dir_is_linked():
    logging.info('Linking {} to VBox disk (if it is not already linked)'.format(constants.VM_PERSIST_DIR))
    mkdir_if_cmd = 'if [ ! -d /mnt/sda1{0} ]; then sudo mkdir /mnt/sda1{0}; fi'.format(constants.VM_PERSIST_DIR)
    mount_if_cmd = 'if [ ! -d {0} ]; then sudo ln -s /mnt/sda1{0} {0}; fi'.format(constants.VM_PERSIST_DIR)
    check_and_log_output_and_error_demoted(['boot2docker', 'ssh', mkdir_if_cmd])
    check_and_log_output_and_error_demoted(['boot2docker', 'ssh', mount_if_cmd])

def _ensure_cp_dir_exists():
    logging.info('Creating {} in VM to support dusty cp'.format(constants.VM_CP_DIR))
    mkdir_if_cmd = 'if [ ! -d {0} ]; then sudo mkdir {0}; fi'.format(constants.VM_CP_DIR)
    check_and_log_output_and_error_demoted(['boot2docker', 'ssh', mkdir_if_cmd])

def _ensure_docker_vm_exists():
    """Initialize the boot2docker VM if it does not already exist."""
    logging.info('Initializing boot2docker, this will take a while the first time it runs')
    check_and_log_output_and_error_demoted(['boot2docker', 'init'])

def _ensure_docker_vm_is_started():
    """Start the boot2docker VM if it is not already running."""
    logging.info('Making sure the boot2docker VM is started')
    check_and_log_output_and_error_demoted(['boot2docker', 'start'])

def initialize_docker_vm():
    _ensure_docker_vm_exists()
    _ensure_docker_vm_is_started()
    _ensure_rsync_is_installed()
    _ensure_persist_dir_is_linked()
    _ensure_cp_dir_exists()

def get_docker_vm_ip():
    """Checks boot2docker's IP, assuming that the VM is started"""
    logging.info("Checking boot2docker's ip")
    ip = check_and_log_output_and_error_demoted(['boot2docker', 'ip']).rstrip()
    return ip

def _format_df_line(line):
    split_line = line.split()
    usage_pct = split_line[4]
    total = split_line[1]
    used = split_line[2]
    free = split_line[3]
    formatted_usage = "Usage: {}\n".format(usage_pct)
    formatted_usage += "Total Size: {}\n".format(total)
    formatted_usage += "Used: {}\n".format(used)
    formatted_usage += "Free: {}".format(free)
    return formatted_usage

def get_docker_vm_disk_info():
    df_output = check_output_demoted(['boot2docker', 'ssh', 'df', '-h', '|', 'grep', '/dev/sda1'])
    output_lines = df_output.split('\n')
    return _format_df_line(output_lines[0])
