import os
import re
import logging
import subprocess

from ... import constants
from ...config import get_config_value, assert_config_key
from ...demote import check_and_log_output_and_error_demoted, check_output_demoted
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

def _ensure_docker_vm_exists():
    """Initialize the boot2docker VM if it does not already exist."""
    logging.info('Initializing boot2docker, this will take a while the first time it runs')
    check_and_log_output_and_error_demoted(['boot2docker', 'init'])

def _ensure_docker_vm_is_started():
    """Start the boot2docker VM if it is not already running."""
    logging.info('Making sure the boot2docker VM is started')
    check_and_log_output_and_error_demoted(['boot2docker', 'start'])

def initialize_docker_vm():
    assert_config_key('mac_username')
    _ensure_docker_vm_exists()
    _ensure_docker_vm_is_started()
    _ensure_rsync_is_installed()
    _ensure_persist_dir_is_linked()

def get_docker_vm_ip():
    """Checks boot2docker's IP, assuming that the VM is started"""
    logging.info("Checking boot2docker's ip")
    maybe_ip = check_and_log_output_and_error_demoted(['boot2docker', 'ip']).rstrip()
    print "MAYBEIP: {}".format(maybe_ip)
    return maybe_ip
