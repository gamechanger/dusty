import os

from prettytable import PrettyTable

from ..config import get_config_value, save_config_value
from ..compiler.spec_assembler import get_specs, get_specs_repo, get_all_repos, get_assembled_specs
from ..source import Repo
from ..log import log_to_client
from .. import constants
from ..payload import daemon_command

@daemon_command
def list_repos():
    repos, overrides = get_all_repos(), get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY)
    table = PrettyTable(['Full Name', 'Short Name', 'Local Override'])
    for repo in repos:
        table.add_row([repo.remote_path, repo.short_name,
                       repo.override_path if repo.is_overridden else ''])
    log_to_client(table.get_string(sortby='Full Name'))

@daemon_command
def override_repo(repo_name, source_path):
    repo = Repo.resolve(get_all_repos(), repo_name)
    if not os.path.exists(source_path):
        raise OSError('Source path {} does not exist'.format(source_path))
    config = get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY)
    config[repo.remote_path] = source_path
    save_config_value(constants.CONFIG_REPO_OVERRIDES_KEY, config)
    log_to_client('Locally overriding repo {} to use source at {}'.format(repo.remote_path, source_path))

def _manage_repo(repo_name):
    repo = Repo.resolve(get_all_repos(), repo_name)
    config = get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY)
    if repo.remote_path in config:
        del config[repo.remote_path]
        save_config_value(constants.CONFIG_REPO_OVERRIDES_KEY, config)
        log_to_client('Will manage repo {} with Dusty-managed copy of source'.format(repo.remote_path))
    else:
        log_to_client('No overriden repos found by name {}'.format(repo_name))


@daemon_command
def manage_repo(repo_name):
    _manage_repo(repo_name)

@daemon_command
def manage_all_repos():
    for repo in get_all_repos():
        if repo.remote_path in get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY).keys():
            _manage_repo(repo.remote_path)

@daemon_command
def override_repos_from_directory(source_path):
    log_to_client('Overriding all repos found at {}'.format(source_path))
    for repo in get_all_repos():
        repo_path = os.path.join(source_path, repo.short_name)
        if os.path.isdir(repo_path):
            override_repo(repo.remote_path, repo_path)

@daemon_command
def update_managed_repos():
    """For any active, managed repos, update the Dusty-managed
    copy to bring it up to date with the latest master."""
    log_to_client('Pulling latest updates for all active managed repos:')
    overrides = set(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY))
    specs_repo = get_specs_repo()
    if not specs_repo.is_overridden:
        log_to_client('Updating managed copy of specs-repo before loading specs')
        specs_repo.update_local_repo()
    for repo in get_all_repos(active_only=True, include_specs_repo=False):
        if not repo.is_overridden:
            log_to_client('Updating managed copy of {}'.format(repo.remote_path))
            repo.update_local_repo()
