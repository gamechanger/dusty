# coding=utf-8

import os
import tempfile
import shutil

from mock import patch, call

from dusty.config import get_config_value
from dusty.commands.bundles import activate_bundle
from dusty.commands.repos import (list_repos, override_repo, manage_repo,
                                  override_repos_from_directory, update_managed_repos)
from dusty.compiler.spec_assembler import get_specs_repo
from ...testcases import DustyTestCase
from dusty import constants

class TestReposCommands(DustyTestCase):
    def setUp(self):
        super(TestReposCommands, self).setUp()
        os.mkdir(os.path.join(self.temp_repos_path, 'a'))
        os.mkdir(os.path.join(self.temp_repos_path, 'b'))

    def _assert_listed_repos(self, result, repo_override_tuples):
        for index, repo_override in enumerate(repo_override_tuples):
            repo, override = repo_override
            output_row = index + 3
            self.assertIn(repo, result.splitlines()[output_row])
            if override:
                self.assertIn(override, result.splitlines()[output_row])

    def test_list_repos_with_no_overrides(self):
        list_repos()
        self._assert_listed_repos(self.last_client_output,
                                  [['github.com/app/a', False],
                                   ['github.com/app/b', False]])

    def test_list_repos_with_one_override(self):
        override_repo('github.com/app/a', self.temp_specs_path)
        list_repos()
        self._assert_listed_repos(self.last_client_output,
                                  [['github.com/app/a', self.temp_specs_path],
                                   ['github.com/app/b', False]])

    def test_list_repos_with_both_overridden(self):
        override_repo('github.com/app/a', self.temp_specs_path)
        override_repo('github.com/app/b', self.temp_specs_path)
        list_repos()
        self._assert_listed_repos(self.last_client_output,
                                  [['github.com/app/a', self.temp_specs_path],
                                   ['github.com/app/b', self.temp_specs_path]])

    def test_override_repo(self):
        override_repo('github.com/app/a', self.temp_specs_path)
        self.assertItemsEqual(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY), {get_specs_repo(): self.temp_specs_path,
                                                                   'github.com/app/a': self.temp_specs_path})

    def test_override_then_manage_repo(self):
        override_repo('github.com/app/a', self.temp_specs_path)
        self.assertItemsEqual(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY), {get_specs_repo(): self.temp_specs_path,
                                                                   'github.com/app/a': self.temp_specs_path})
        manage_repo('github.com/app/a')
        self.assertItemsEqual(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY), {get_specs_repo(): self.temp_specs_path})

    def test_override_repos_from_directory(self):
        override_repos_from_directory(self.temp_repos_path)
        self.assertItemsEqual(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY), {get_specs_repo(): self.temp_specs_path,
                                                                   'github.com/app/a': os.path.join(self.temp_repos_path, 'a'),
                                                                   'github.com/app/b': os.path.join(self.temp_repos_path, 'b'),
                                                                   'github.com/lib/a': os.path.join(self.temp_repos_path, 'a')})

    @patch('dusty.commands.repos.update_local_repo')
    def test_update_managed_repos(self, fake_update_local_repo):
        activate_bundle(['bundle-a'])
        update_managed_repos()
        fake_update_local_repo.assert_called_once_with('github.com/app/a')

    @patch('dusty.commands.repos.update_local_repo')
    def test_update_managed_repos_for_both(self, fake_update_local_repo):
        activate_bundle(['bundle-a'])
        activate_bundle(['bundle-b'])
        update_managed_repos()
        fake_update_local_repo.assert_has_calls([call('github.com/app/a'), call('github.com/app/b')])
