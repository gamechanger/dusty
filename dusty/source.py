"""Module for managing the versions of applications' source
repositories managed by Dusty itself."""

import os
import logging

import git

from .constants import GIT_USER, REPOS_PATH
from .notifier import notify

def _repo_path(repo_name):
    return os.path.join(REPOS_PATH, repo_name)

def _short_repo_name(repo_name):
    return repo_name.split('/')[-1]

def ensure_local_repo(repo_name):
    """Given a repo name (e.g. github.com/gamechanger/gclib), clone the
    repo into Dusty's local repos directory if it does not already exist."""
    repo_path = _repo_path(repo_name)
    if os.path.exists(repo_path):
        logging.debug('Repo {} already exists'.format(repo_name))
        return

    logging.info('Initiating clone of local repo {}'.format(repo_name))
    notify('Cloning repository {}'.format(_short_repo_name(repo_name)))

    repo_path_parent = os.path.split(repo_path)[0]
    if not os.path.exists(repo_path_parent):
        os.makedirs(repo_path_parent)
    repo = git.Repo.clone_from('ssh://{}@{}'.format(GIT_USER, repo_name), repo_path)

def update_local_repo(repo_name):
    """Given a repo name (e.g. github.com/gamechanger/gclib), pull the latest
    commits from master to bring the local copy up to date."""
    ensure_local_repo(repo_name)

    logging.info('Updating local repo {}'.format(repo_name))
    notify('Pulling latest updates for {}'.format(_short_repo_name(repo_name)))

    repo_path = _repo_path(repo_name)
    repo = git.Repo(repo_path)
    repo.remote().pull('master')
