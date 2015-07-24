import os
import re
import logging
import textwrap

from ... import constants
from ...config import get_config_value
from ...subprocess import check_and_log_output_and_error_demoted, check_output_demoted, check_call_demoted, call_demoted
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

def _init_docker_vm():
    """Initialize the boot2docker VM if it does not already exist."""
    logging.info('Initializing boot2docker, this will take a while the first time it runs')
    check_call_demoted(['boot2docker', 'init'], redirect_stderr=True)

def _start_docker_vm():
    """Start the boot2docker VM if it is not already running."""
    logging.info('Making sure the boot2docker VM is started')
    memory_size = int(get_config_value(constants.CONFIG_VM_MEM_SIZE))
    call_demoted(['VBoxManage', 'modifyvm', 'boot2docker-vm', '--memory', '{}'.format(memory_size)])
    check_call_demoted(['boot2docker', 'start'], redirect_stderr=True)

def ensure_docker_vm_is_started():
    _init_docker_vm()
    _start_docker_vm()

def _apply_1_7_cert_hack():
    """boot2docker 1.7 has been a total disaster. One of the upgrade problems is that
    the certificates used for TLS to the Docker client become invalid. There's some sort
    of race condition here which is fixed by this hack.
    Issue: https://github.com/boot2docker/boot2docker/issues/938
    Hack: https://github.com/boot2docker/boot2docker/issues/824#issuecomment-113904164
    """
    hack = textwrap.dedent("""
    wait4eth1() {
        CNT=0
        until ip a show eth1 | grep -q UP
        do
                [ $((CNT++)) -gt 60 ] && break || sleep 1
        done
        sleep 1
    }
    wait4eth1""")
    if call_demoted(['boot2docker', 'ssh', 'test -f /var/lib/boot2docker/profile']) != 0:
        log_to_client('Applying boot2docker 1.7 cert hack')
        check_and_log_output_and_error_demoted(['boot2docker', 'ssh',
                                                'sudo sh -c \'printf \"{}\" > /var/lib/boot2docker/profile\''.format(hack)])
        check_and_log_output_and_error_demoted(['boot2docker', 'ssh', 'sudo /etc/init.d/docker restart'])

def initialize_docker_vm():
    ensure_docker_vm_is_started()
    _apply_1_7_cert_hack()
    _ensure_rsync_is_installed()
    _ensure_persist_dir_is_linked()
    _ensure_cp_dir_exists()

def get_docker_vm_ip():
    """Checks boot2docker's IP, assuming that the VM is started"""
    logging.info("Checking boot2docker's ip")
    ip = check_output_demoted(['boot2docker', 'ip']).rstrip()
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
