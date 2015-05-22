import os
import re
import logging
import subprocess

from ... import constants
from ...config import get_config_value, assert_config_key
from ...demote import check_and_log_output_and_error_demoted, check_output_demoted

logger = logging.getLogger(constants.SOCKET_LOGGER_NAME)

def _name_for_rule(forwarding_spec, protocol):
    return '{}_{}_{}'.format(constants.VIRTUALBOX_RULE_PREFIX, forwarding_spec['host_port'], protocol)

def _add_forwarding_rules(forwarding_spec):
    """Add TCP and UDP forwarding rules from the host OS to
    the Docker VM in VirtualBox, according to the forwarding spec
    passed down from the port compiler."""
    logging.info('Adding local forwarding rules from spec: {}'.format(forwarding_spec))
    for protocol in ['tcp', 'udp']:
        rule_spec = '{},{},{},{},{},{}'.format(_name_for_rule(forwarding_spec, protocol),
                                               protocol,
                                               forwarding_spec['host_ip'],
                                               forwarding_spec['host_port'],
                                               forwarding_spec['guest_ip'],
                                               forwarding_spec['guest_port'])
        message = 'Adding local forwarding rule: {}'.format(rule_spec)
        logger.info(message)
        check_and_log_output_and_error_demoted(['VBoxManage', 'controlvm', 'boot2docker-vm', 'natpf1', rule_spec])

def _remove_existing_forwarding_rules(forwarding_spec):
    """Remove any existing forwarding rule that may exist for the given
    host port. It's possible to get VirtualBox to list out the current rules,
    but that's got a race condition built into it, so our approach is
    to try to delete the rule and swallow the exception if the rule
    did not exist in the first place."""
    logging.info('Removing local forwarding rules from spec: {}'.format(forwarding_spec))
    for protocol in ['tcp', 'udp']:
        try:
            check_and_log_output_and_error_demoted(['VBoxManage', 'controlvm', 'boot2docker-vm',
                                 'natpf1', 'delete', _name_for_rule(forwarding_spec, protocol)])
        except subprocess.CalledProcessError:
            logging.warning('Deleting rule failed, possibly because it did not exist. Continuing...')

def _ensure_rsync_is_installed():
    logging.info('Installing rsync inside the Docker VM')
    check_call_demoted(['boot2docker', 'ssh', 'tce-load -wi rsync'])

def _ensure_persist_dir_is_linked():
    logging.info('Linking {} to VBox disk (if it is not already linked)'.format(constants.VM_PERSIST_DIR))
    mkdir_if_cmd = 'if [ ! -d /mnt/sda1{0} ]; then sudo mkdir /mnt/sda1{0}; fi'.format(constants.VM_PERSIST_DIR)
    mount_if_cmd = 'if [ ! -d {0} ]; then sudo ln -s /mnt/sda1{0} {0}; fi'.format(constants.VM_PERSIST_DIR)
    check_and_log_output_and_error_demoted(['boot2docker', 'ssh', mkdir_if_cmd])
    check_and_log_output_and_error_demoted(['boot2docker', 'ssh', mount_if_cmd])

def _ensure_dusty_shared_folder_exists():
    """Create the dusty shared folder in the boot2docker VM if it does
    not already exist. Creating shared folders requires the VM to
    be powered down."""
    if not _dusty_shared_folder_already_exists():
        logging.info('Stopping boot2docker VM to allow creation of shared volume')
        check_and_log_output_and_error_demoted(['boot2docker', 'stop'])
        logging.info('Creating dusty shared folder inside boot2docker VM')
        check_and_log_output_and_error_demoted(['VBoxManage', 'sharedfolder', 'add', 'boot2docker-vm',
                             '--name', 'dusty', '--hostpath', constants.CONFIG_DIR])

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

def update_virtualbox_port_forwarding_from_port_spec(port_spec):
    """Update the current VirtualBox port mappings from the host OS
    to the VM to reflect the given port_spec. Overwrites any
    previous rules set on ports needed by the new spec."""
    assert_config_key('mac_username')
    logging.info('Updating port forwarding rules in VirtualBox')
    virtualbox_specs = port_spec['virtualbox']
    for forwarding_spec in virtualbox_specs:
        _remove_existing_forwarding_rules(forwarding_spec)
        _add_forwarding_rules(forwarding_spec)
