import logging
import subprocess

from ... import constants

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
        logging.info('Adding local forwarding rule: {}'.format(rule_spec))
        subprocess.check_call(['VBoxManage', 'controlvm', 'boot2docker-vm', 'natpf1', rule_spec])

def _remove_existing_forwarding_rules(forwarding_spec):
    """Remove any existing forwarding rule that may exist for the given
    host port. It's possible to get VirtualBox to list out the current rules,
    but that's got a race condition built into it, so our approach is
    to try to delete the rule and swallow the exception if the rule
    did not exist in the first place."""
    logging.info('Removing local forwarding rules from spec: {}'.format(forwarding_spec))
    for protocol in ['tcp', 'udp']:
        try:
            subprocess.check_call(['VBoxManage', 'controlvm', 'boot2docker-vm',
                                   'natpf1', 'delete', _name_for_rule(forwarding_spec, protocol)])
        except subprocess.CalledProcessError:
            logging.warning('Deleting rule failed, possibly because it did not exist. Continuing...')

def update_virtualbox_port_forwarding_from_port_spec(port_spec):
    """Update the current VirtualBox port mappings from the host OS
    to the VM to reflect the given port_spec. Overwrites any
    previous rules set on ports needed by the new spec."""
    logging.info('Updating port forwarding rules in VirtualBox')
    virtualbox_specs = port_spec['virtualbox']
    for forwarding_spec in virtualbox_specs:
        _remove_existing_forwarding_rules(forwarding_spec)
        _add_forwarding_rules(forwarding_spec)
