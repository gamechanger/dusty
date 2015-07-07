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

def _pretty_print_key_info(config_key):
    print '{}: {}\n'.format(config_key, '\n'.join(textwrap.wrap(constants.CONFIG_SETTINGS[config_key], 80)))

def _get_raw_input(string):
    return raw_input(string).strip()

def _get_mac_username():
    _pretty_print_key_info(constants.CONFIG_MAC_USERNAME_KEY)
    proposed_mac_username = subprocess.check_output(['id', '-un']).strip()
    if _get_raw_input("Is {} the username under which you'll primarily use Dusty? (y/n): ".format(proposed_mac_username)).upper() == 'Y':
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

def _setup_nginx_config(nginx_conf_location):
    include_path = '{}/servers'.format(nginx_conf_location)
    if not isdir(include_path):
        mkdir(include_path)
    _append_to_file('{}/nginx.conf'.format(nginx_conf_location), '\ninclude servers/*;\n')
    return include_path

def _get_and_configure_nginx_includes_dir():
    for nginx_conf_location in constants.NGINX_CONFIG_FILE_LOCATIONS:
        file_location = '{}/nginx.conf'.format(nginx_conf_location)
        if isfile(file_location):
            contents = _get_contents_of_file(file_location)
            for line in contents:
                if line.startswith('include'):
                    include_folder = line.replace('include ', '').replace('/*;', '').replace('\n', '').strip()
                    return '{}/{}'.format(nginx_conf_location, include_folder)
            if _get_raw_input('\n'.join(textwrap.wrap('You have non standard nginx config setup. Can we add "include servers/*;" to the end of your nginx config file ({})? If you select no, your nginx forwarding will not work. (y/n) '.format(file_location), 80))).upper() == 'Y':
                return _setup_nginx_config(nginx_conf_location)
            else:
                return ''
    _get_raw_input('\n'.join(textwrap.wrap('You have a custom nginx config setup. Could not find an nginx.conf file. Please read our docs to see what is needed for the nginx config.  Once you have figured it out, please use `dusty config` command to adjust your `nginx_includes_dir`', 80)))
    return ''

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
    if _get_raw_input('Your system seems to have {} megabytes of memory. We would like to allocate {} to your vm. Is that ok? (y/n) '.format(memory_megs, vm_megs)).upper() == 'Y':
        return vm_megs
    else:
        return _get_raw_input('Please input the number of megabytes to allocate to the vm: ')

def setup_dusty_config(mac_username=None, specs_repo=None, nginx_includes_dir=None, boot2docker_vm_memory=None):
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

    if nginx_includes_dir:
        print 'Setting nginx_includes_dir to {} based on flag'.format(nginx_includes_dir)
    else:
        nginx_includes_dir = _get_and_configure_nginx_includes_dir()

    if boot2docker_vm_memory:
        print 'Setting boot2docker_vm_memory to {} based on flag'.format(boot2docker_vm_memory)
    else:
        boot2docker_vm_memory = _get_boot2docker_vm_size()

    boot2docker_vm_memory = int(boot2docker_vm_memory)

    config_dictionary = {constants.CONFIG_MAC_USERNAME_KEY: mac_username,
                         constants.CONFIG_SPECS_REPO_KEY: specs_repo,
                         constants.CONFIG_NGINX_DIR_KEY: nginx_includes_dir,
                         constants.CONFIG_VM_MEM_SIZE: boot2docker_vm_memory}
    payload = Payload(complete_setup, config_dictionary)
    payload.suppress_warnings = True
    return payload

@daemon_command
def complete_setup(config):
    for key, value in config.iteritems():
        save_config_value(key, value)
    save_config_value(constants.CONFIG_SETUP_KEY, True)
    refresh_config_warnings()
    update_managed_repos()
    log_to_client('Initial setup completed. You should now be able to use Dusty!')
