from .compiler.spec_assembler import get_repo_of_app_or_library, get_expanded_libs_specs
from .config import get_config_value, save_config_value
from . import constants

class RepoChangeSet(object):
    """Used for keeping track of the latest SHAs seen for a set
    of repos during a given operation. The observed SHAs are persisted
    in the Dusty config.

    One example of what you could use this for is to answer the question,
    "Have any of the dependent repos for this app changed since the last
    time I made a testing image for it?" You could make a changeset for
    that this way:

    RepoChangeSet('testing_image_myapp', 'myapp')
    """
    def __init__(self, set_key, app_or_library_name):
        self.set_key = set_key
        self.app_or_library_name = app_or_library_name
        self.repos = {get_repo_of_app_or_library(self.app_or_library_name)}
        for lib_name in self.primary_spec['depends']['libs']:
            self.repos.add(get_repo_of_app_or_library(lib_name))

    @property
    def primary_spec(self):
        expanded_specs = get_expanded_libs_specs()
        if self.app_or_library_name in expanded_specs['apps']:
            return expanded_specs['apps'][self.app_or_library_name]
        return expanded_specs['libs'][self.app_or_library_name]

    def _get_current_sha_dict(self):
        return {repo.remote_path: repo.local_commit_sha
                for repo in self.repos}

    def has_changed(self):
        stored = get_config_value(constants.CONFIG_CHANGESET_KEY) or {}
        return self._get_current_sha_dict() != stored.get(self.set_key, {})

    def update(self):
        stored = get_config_value(constants.CONFIG_CHANGESET_KEY) or {}
        stored[self.set_key] = self._get_current_sha_dict()
        save_config_value(constants.CONFIG_CHANGESET_KEY, stored)
