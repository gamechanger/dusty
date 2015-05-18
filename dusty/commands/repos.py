import os

from prettytable import PrettyTable

from ..config import get_config_value, save_config_value
from ..specs import get_specs
from ..compiler.spec_assembler import get_assembled_specs
from ..source import update_local_repo

def _get_all_repos(active_only=False):
    repos = set()
    specs = get_assembled_specs() if active_only else get_specs()
    for type_key in ['apps', 'libs']:
        for spec in specs[type_key].itervalues():
            if 'repo' in spec:
                repos.add(spec['repo'])
    return repos

def list_repos():
    repos, overrides = _get_all_repos(), get_config_value('repo_overrides')
    table = PrettyTable(['Name', 'Local Override'])
    for repo in repos:
        table.add_row([repo,
                       overrides[repo] if repo in overrides else ''])
    yield table.get_string(sortby='Name')

def override_repo(repo_name, source_path):
    repos = _get_all_repos()
    if repo_name not in repos:
        raise KeyError('No repo registered named {}'.format(repo_name))
    if not os.path.exists(source_path):
        raise OSError('Source path {} does not exist'.format(source_path))
    config = get_config_value('repo_overrides') or {}
    config[repo_name] = source_path
    save_config_value('repo_overrides', config)
    yield 'Locally overriding repo {} to use source at {}'.format(repo_name, source_path)

def manage_repo(repo_name):
    repos = _get_all_repos()
    if repo_name not in repos:
        raise KeyError('No repo registered named {}'.format(repo_name))
    config = get_config_value('repo_overrides')
    if repo_name in config:
        del config[repo_name]
    save_config_value('repo_overrides', config)
    yield 'Will manage repo {} with Dusty-managed copy of source'.format(repo_name)

def override_repos_from_directory(source_path):
    yield 'Overriding all repos found at {}'.format(source_path)
    for repo in _get_all_repos():
        repo_name = repo.split('/')[-1]
        repo_path = os.path.join(source_path, repo_name)
        if os.path.isdir(repo_path):
            for result in override_repo(repo, repo_path):
                yield result

def update_managed_repos():
    """For any active, managed repos, update the Dusty-managed
    copy to bring it up to date with the latest master."""
    yield 'Pulling latest updates for all active managed repos'
    overrides = set(get_config_value('repo_overrides'))
    for repo_name in _get_all_repos(active_only=True):
        if repo_name not in overrides:
            yield 'Updating managed copy of {}'.format(repo_name)
            update_local_repo(repo_name)
