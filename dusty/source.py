"""Module for managing the versions of applications' source
repositories managed by Dusty itself."""

import os
import logging
from contextlib import contextmanager

import git

from .config import get_config_value
from . import constants
from .notifier import notify
from .log import log_to_client
from .compiler.spec_assembler import get_all_repos

def repo_is_overridden(repo_name):
    return repo_name in get_config_value('repo_overrides')

def local_repo_path(repo_name):
    """Given a repo_name (github.com/gamechanger/gclib), checks if that repo has an
    override, and returns the appropriate directory"""
    repo_overrides = get_config_value('repo_overrides')
    override_dir = repo_overrides.get(repo_name)
    return override_dir if override_dir else _managed_repo_path(repo_name)

def vm_repo_path(repo_name):
    return os.path.join(constants.VM_REPOS_DIR, repo_name)

def _managed_repo_path(repo_name):
    return os.path.join(constants.REPOS_DIR, repo_name)

def short_repo_name(repo_name):
    return repo_name.split('/')[-1]

def _is_short_name(repo_name):
    return '/' not in repo_name

def _expand_repo_name(passed_short_name):
    match = None
    for repo_name in get_all_repos():
        short_name = short_repo_name(repo_name)
        if passed_short_name == short_name and match is None:
            match = repo_name
        elif passed_short_name == short_name:
            raise RuntimeError('Short repo name {} is ambiguous. It matches both {} and {}'.format(passed_short_name, match, repo_name))
    if match is None:
        raise RuntimeError("Short repo name {} does not match any full repo names".format(passed_short_name))
    else:
        return match

def get_expanded_repo_name(repo_name):
    if _is_short_name(repo_name):
        return _expand_repo_name(repo_name)
    return repo_name

@contextmanager
def git_error_handling():
    try:
        yield
    except git.exc.GitCommandError:
        log_to_client('ERROR: Git command failed. If you are trying to access a private repo, '
                      'please make sure you have added your SSH key to the SSH agent using: '
                      'ssh-add <SSH key filepath>')
        raise

def ensure_local_repo(repo_name):
    """Given a repo name (e.g. github.com/gamechanger/gclib), clone the
    repo into Dusty's local repos directory if it does not already exist."""
    repo_path = _managed_repo_path(repo_name)
    if os.path.exists(repo_path):
        logging.debug('Repo {} already exists'.format(repo_name))
        return

    logging.info('Initiating clone of local repo {}'.format(repo_name))
    notify('Cloning repository {}'.format(short_repo_name(repo_name)))

    repo_path_parent = os.path.split(repo_path)[0]
    if not os.path.exists(repo_path_parent):
        os.makedirs(repo_path_parent)
    with git_error_handling():
        repo = git.Repo.clone_from('ssh://{}@{}'.format(constants.GIT_USER, repo_name), repo_path)

def update_local_repo(repo_name):
    """Given a repo name (e.g. github.com/gamechanger/gclib), pull the latest
    commits from master to bring the local copy up to date."""
    ensure_local_repo(repo_name)

    logging.info('Updating local repo {}'.format(repo_name))
    notify('Pulling latest updates for {}'.format(short_repo_name(repo_name)))

    repo_path = _managed_repo_path(repo_name)
    repo = git.Repo(repo_path)
    with git_error_handling():
        repo.remote().pull('master')
