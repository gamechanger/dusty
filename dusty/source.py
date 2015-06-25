"""Module for managing the versions of applications' source
repositories managed by Dusty itself."""

import os
import logging
from contextlib import contextmanager

import git

from .config import get_config_value
from . import constants
from .log import log_to_client
from .path import parent_dir

@contextmanager
def git_error_handling():
    try:
        yield
    except git.exc.GitCommandError:
        log_to_client('ERROR: Git command failed. If you are trying to access a private repo, '
                      'please make sure you have added your SSH key to the SSH agent using: '
                      'ssh-add <SSH key filepath>')
        raise

class Repo(object):
    def __init__(self, remote_path):
        # remote path is either of actual remote (github.com/gamechanger/dusty) or
        # other local repo (/repos/dusty) format
        self.remote_path = remote_path

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.remote_path == other.remote_path
        return False

    def __hash__(self):
        return hash(self.remote_path)

    @classmethod
    def resolve(cls, all_known_repos, name):
        """We require the list of all remote repo paths to be passed in
        to this because otherwise we would need to import the spec assembler
        in this module, which would give us circular imports."""
        match = None
        for repo in all_known_repos:
            if repo.remote_path == name: # user passed in a full name
                return repo
            if name == repo.short_name:
                if match is None:
                    match = repo
                else:
                    raise RuntimeError('Short repo name {} is ambiguous. It matches both {} and {}'.format(name,
                                                                                                           match.remote_path,
                                                                                                           repo.remote_path))
        if match is None:
            raise RuntimeError('Short repo name {} does not match any known repos'.format(name))
        return match

    @property
    def is_local_repo(self):
        return self.remote_path.startswith('/')

    @property
    def short_name(self):
        return self.remote_path.split('/')[-1]

    @property
    def managed_path(self):
        return os.path.join(constants.REPOS_DIR, self.remote_path.lstrip('/'))

    @property
    def is_overridden(self):
        return self.remote_path in get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY)

    @property
    def override_path(self):
        repo_overrides = get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY)
        return repo_overrides.get(self.remote_path)

    @property
    def local_path(self):
        return self.override_path if self.is_overridden else self.managed_path

    @property
    def vm_path(self):
        return os.path.join(constants.VM_REPOS_DIR, self.remote_path.lstrip('/'))

    def ensure_local_repo(self):
        """Given a Dusty repo object, clone the remote into Dusty's local repos
        directory if it does not already exist."""
        if os.path.exists(self.managed_path):
            logging.debug('Repo {} already exists'.format(self.remote_path))
            return

        logging.info('Initiating clone of local repo {}'.format(self.remote_path))

        repo_path_parent = parent_dir(self.managed_path)
        if not os.path.exists(repo_path_parent):
            os.makedirs(repo_path_parent)
        with git_error_handling():
            if self.is_local_repo:
                git.Repo.clone_from('file:///{}'.format(self.remote_path), self.managed_path)
            else:
                git.Repo.clone_from('ssh://{}@{}'.format(constants.GIT_USER, self.remote_path), self.managed_path)

    def update_local_repo(self):
        """Given a remote path (e.g. github.com/gamechanger/gclib), pull the latest
        commits from master to bring the local copy up to date."""
        self.ensure_local_repo()

        logging.info('Updating local repo {}'.format(self.remote_path))
        print self.managed_path

        managed_repo = git.Repo(self.managed_path)
        with git_error_handling():
            managed_repo.remote().pull('master')
