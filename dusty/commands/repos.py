import os

from prettytable import PrettyTable

from ..config import get_config_value, save_config_value
from ..specs import get_specs

def _get_all_repos():
    specs, repos = get_specs(), set()
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
    config = get_config_value('repo_overrides')
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
