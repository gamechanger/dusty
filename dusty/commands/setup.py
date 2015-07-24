import pwd
import subprocess
import textwrap
from os.path import isfile, isdir
from os import mkdir

from psutil import virtual_memory

from ..payload import Payload
from ..config import save_config_value, get_config_value, verify_mac_username, refresh_config_warnings
from ..log import log_to_client
from .. import constants
from .repos import update_managed_repos
from ..payload import daemon_command

def _is_yes_response(response):
    return response == 'y' or response == 'Y' or response == ''

def _pretty_print_key_info(config_key):
    print '{}: {}\n'.format(config_key, '\n'.join(textwrap.wrap(constants.CONFIG_SETTINGS[config_key], 80)))

def _get_raw_input(string):
    return raw_input(string).strip()

def _get_mac_username():
    _pretty_print_key_info(constants.CONFIG_MAC_USERNAME_KEY)
    proposed_mac_username = subprocess.check_output(['id', '-un']).strip()
    response  = _get_raw_input("Is {} the username under which you'll primarily use Dusty? (y/n): ".format(proposed_mac_username))
    if _is_yes_response(response):
        return proposed_mac_username
    else:
        return _get_raw_input('Enter your actual mac_username: ')

def _get_specs_repo():
    _pretty_print_key_info(constants.CONFIG_SPECS_REPO_KEY)
    print 'Repos may be specified with a URL (e.g. github.com/org/repo) or an absolute file path to a local repository'
    specs_repo = _get_raw_input('Input the path to your specs repo, or leave blank to start with the example specs: ')
    if not specs_repo:
        print 'Using example specs repo {}'.format(constants.EXAMPLE_SPECS_REPO)
        specs_repo = constants.EXAMPLE_SPECS_REPO
    return specs_repo

def _get_contents_of_file(file_location):
    with open(file_location) as f:
        return f.readlines()

def _append_to_file(file_location, new_line):
    with open(file_location, 'a') as f:
        f.write(new_line)

def _get_recommended_vm_size(system_memory):
    # all math is done in megabytes
    if system_memory >= 16 * 2**10:
        return 6 * 2**10
    elif system_memory >= 8 * 2**10:
        return 4 * 2**10
    else:
        return 2 * 2**10

def _get_boot2docker_vm_size():
    memory_megs = virtual_memory().total / 2**20
    vm_megs = _get_recommended_vm_size(memory_megs)
    response = _get_raw_input('Your system seems to have {} megabytes of memory. We would like to allocate {} to your vm. Is that ok? (y/n) '.format(memory_megs, vm_megs))
    if _is_yes_response(response):
        return vm_megs
    else:
        return _get_raw_input('Please input the number of megabytes to allocate to the vm: ')

def setup_dusty_config(mac_username=None, specs_repo=None, boot2docker_vm_memory=None, update=True):
    print "We just need to verify a few settings before we get started.\n"
    if mac_username:
        print 'Setting mac_username to {} based on flag'.format(mac_username)
    else:
        mac_username = _get_mac_username()
    verify_mac_username(mac_username)
    print ''

    if specs_repo:
        print 'Setting specs_repo to {} based on flag'.format(specs_repo)
    else:
        specs_repo = _get_specs_repo()
    print ''

    if boot2docker_vm_memory:
        print 'Setting boot2docker_vm_memory to {} based on flag'.format(boot2docker_vm_memory)
    else:
        boot2docker_vm_memory = _get_boot2docker_vm_size()

    boot2docker_vm_memory = int(boot2docker_vm_memory)

    config_dictionary = {constants.CONFIG_MAC_USERNAME_KEY: mac_username,
                         constants.CONFIG_SPECS_REPO_KEY: specs_repo,
                         constants.CONFIG_VM_MEM_SIZE: boot2docker_vm_memory}
    payload = Payload(complete_setup, config_dictionary, update=update)
    payload.suppress_warnings = True
    return payload

@daemon_command
def complete_setup(config, update=True):
    for key, value in config.iteritems():
        save_config_value(key, value)
    save_config_value(constants.CONFIG_SETUP_KEY, True)
    refresh_config_warnings()
    if update:
        update_managed_repos()
    log_to_client('Initial setup completed. You should now be able to use Dusty!')
