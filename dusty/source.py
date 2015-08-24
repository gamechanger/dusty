"""Module for managing the versions of applications' source
repositories managed by Dusty itself."""

import os
import logging
from contextlib import contextmanager
import urlparse

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
        log_to_client('ERROR: Git command failed. If you are trying to access a remote repository '
                      'over SSH (e.g. GitHub), please make sure you have added your SSH key to the '
                      'SSH agent using: ssh-add <SSH key filepath>.  If you specified to clone the repo '
                      'using HTTP, the repo must be public; private repo access is only supported with '
                      'ssh')
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
        return self.remote_path.startswith('/') or self.remote_path.startswith('file:///')

    @property
    def is_http_repo(self):
        return self.remote_path.startswith('http')

    @property
    def short_name(self):
        short_name = self.remote_path.split('/')[-1]
        if short_name.endswith('.git'):
            short_name = short_name[:-4]
        return short_name

    @property
    def managed_path(self):
        return os.path.join(constants.REPOS_DIR, self.rel_path)

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
        return os.path.join(constants.VM_REPOS_DIR, self.rel_path)

    @property
    def rel_path(self):
        parsed = urlparse.urlparse(self.remote_path.lstrip('/'))
        if parsed.hostname:
            local_folder = parsed.hostname + parsed.path
        else:
            local_folder = parsed.path
        end_of_path = local_folder.split('/')[-1]
        if '.' in end_of_path:
            local_folder = local_folder.replace(end_of_path, end_of_path.split('.')[0])
        return local_folder.lstrip('/')

    def assemble_remote_path(self):
        if self.is_local_repo:
            if self.remote_path.startswith('file:///'):
                return self.remote_path
            else:
                return 'file:///{}'.format(self.remote_path)
        elif self.is_http_repo:
            if self.remote_path.endswith('.git'):
                return self.remote_path
            else:
                return self.remote_path + '.git'
        else:
            if self.remote_path.startswith('ssh://'):
                return self.remote_path
            else:
                return 'ssh://{}@{}'.format(constants.GIT_USER, self.remote_path)

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
            git.Repo.clone_from(self.assemble_remote_path(), self.managed_path)

    def get_latest_commit(self):
        repo = git.Repo(self.managed_path)
        for ref in repo.refs:
            if ref.path == 'refs/remotes/origin/master':
                return ref.commit
        return repo.remote().fetch()[0].commit

    def local_is_up_to_date(self):
        self.ensure_local_repo()
        repo = git.Repo(self.managed_path)
        local_commit = repo.commit()
        latest_commit = self.get_latest_commit()
        return local_commit.hexsha == latest_commit.hexsha

    def update_local_repo(self, force=False):
        """Given a remote path (e.g. github.com/gamechanger/gclib), pull the latest
        commits from master to bring the local copy up to date."""
        self.ensure_local_repo()

        logging.info('Updating local repo {}'.format(self.remote_path))

        managed_repo = git.Repo(self.managed_path)
        with git_error_handling():
            managed_repo.remote().pull('master')
        if not self.local_is_up_to_date():
            if force:
                with git_error_handling():
                    managed_repo.git.reset('--hard', 'origin/master')
            else:
                log_to_client('WARNING: couldn\'t update {} because of local conflicts. '
                              'A container may have modified files in the repos\'s directory. '
                              'Your code generally shouldn\'t be manipulating the contents of your repo folder - '
                              'please fix this and run `dusty up`'.format(self.managed_path))
