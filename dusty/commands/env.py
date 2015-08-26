import os

from prettytable import PrettyTable

from ..log import log_to_client
from ..compiler.spec_assembler import get_assembled_specs, get_specs
from ..config import get_env_config, save_config_value
from .. import constants
from ..payload import daemon_command

def _save_env(env_config):
    save_config_value(constants.CONFIG_ENV_KEY, env_config)

def _assert_app_or_service_exists(app_or_service):
    """
    get_app_or_service will throw a KeyError if the app_or_service
    is not found.
    """
    get_specs().get_app_or_service(app_or_service)

@daemon_command
def list_app_or_service(app_or_service):
    _assert_app_or_service_exists(app_or_service)
    env_dict = get_env_config().get(app_or_service)
    if not env_dict:
        log_to_client('No environment overrides specified for {}'.format(app_or_service))
        return
    table = PrettyTable(["Variable", "Value"])
    for var_name, value in env_dict.iteritems():
        table.add_row([var_name, value])
    log_to_client(table.get_string())

@daemon_command
def list_all():
    env_config = get_env_config()
    if not env_config:
        log_to_client('No environment overrides specified')
        return
    active_containers = set([cont.name for cont in get_assembled_specs().get_apps_and_services()])
    log_to_client('Listing environment overrides for activated apps and services:')
    table = PrettyTable(["App or Service", "Variable", "Value"])
    for app_or_service, env_dict in env_config.iteritems():
        if app_or_service in active_containers:
            for var_name, value in env_dict.iteritems():
                table.add_row([app_or_service, var_name, value])
    log_to_client(table.get_string())



def _env_vars_from_file(filename):
    """
    This code is copied from Docker Compose, so that we're exactly compatible
    with their `env_file` option
    """
    def split_env(env):
        if '=' in env:
            return env.split('=', 1)
        else:
            return env, None
    env = {}
    for line in open(filename, 'r'):
        line = line.strip()
        if line and not line.startswith('#'):
            k, v = split_env(line)
            env[k] = v
    return env

@daemon_command
def set_from_file(app_or_service, local_file_path):
    _assert_app_or_service_exists(app_or_service)
    if not os.access(local_file_path, os.R_OK):
        raise RuntimeError('Path {} does not exist or is not readable'.format(local_file_path))
    env_config = get_env_config()
    if not env_config.get(app_or_service):
        env_config[app_or_service] = {}
    env_from_file = _env_vars_from_file(local_file_path)
    env_config[app_or_service].update(env_from_file)
    _save_env(env_config)
    log_to_client('Successfully saved environment from file {} for {}'.format(local_file_path, app_or_service))

@daemon_command
def set_var(app_or_service, var_name, value):
    _assert_app_or_service_exists(app_or_service)
    env_config = get_env_config()
    if not env_config.get(app_or_service):
        env_config[app_or_service] = {}
    env_config[app_or_service][var_name] = value
    _save_env(env_config)
    log_to_client('Successfully saved {}={} for {}'.format(var_name, value, app_or_service))

@daemon_command
def unset_all(app_or_service):
    _assert_app_or_service_exists(app_or_service)
    env_config = get_env_config()
    env_config[app_or_service] = {}
    _save_env(env_config)

@daemon_command
def unset_var(app_or_service, var_name):
    _assert_app_or_service_exists(app_or_service)
    env_config = get_env_config()
    if not env_config.get(app_or_service, {}).get(var_name):
        log_to_client('Variable {} isn\'t set for {}'.format(var_name, app_or_service))
        return
    del env_config[app_or_service][var_name]
    _save_env(env_config)
    log_to_client('Successfully deleted variable {} from {}'.format(var_name, app_or_service))
