import os
import tempfile
import shutil

from mock import patch, call

from dusty.config import get_config_value
from dusty.commands.bundles import activate_bundle
from dusty.commands.repos import (list_repos, override_repo, manage_repo, manage_all_repos,
                                  override_repos_from_directory, update_managed_repos)
from dusty.compiler.spec_assembler import get_specs_repo
from ...testcases import DustyTestCase
from dusty import constants

class TestReposCommands(DustyTestCase):
    def setUp(self):
        super(TestReposCommands, self).setUp()
        os.mkdir(os.path.join(self.temp_repos_path, 'a'))
        os.mkdir(os.path.join(self.temp_repos_path, 'b'))

    def _assert_listed_repos(self, result, repo_override_tuples, offset=0):
        for index, repo_override in enumerate(repo_override_tuples):
            repo, override = repo_override
            output_row = index + 3 + offset
            self.assertIn(repo, result.splitlines()[output_row])
            if override:
                self.assertIn(override, result.splitlines()[output_row])

    def test_list_repos_with_no_overrides(self):
        list_repos()
        self._assert_listed_repos(self.last_client_output,
                                  [['github.com/app/a', False],
                                   ['github.com/app/b', False]],
                                  offset=1)

    def test_list_repos_with_one_override(self):
        override_repo('github.com/app/a', self.temp_specs_path)
        list_repos()
        self._assert_listed_repos(self.last_client_output,
                                  [['github.com/app/a', self.temp_specs_path],
                                   ['github.com/app/b', False]],
                                  offset=1)

    def test_list_repos_with_both_overridden(self):
        override_repo('github.com/app/a', self.temp_specs_path)
        override_repo('github.com/app/b', self.temp_specs_path)
        list_repos()
        self._assert_listed_repos(self.last_client_output,
                                  [['github.com/app/a', self.temp_specs_path],
                                   ['github.com/app/b', self.temp_specs_path]],
                                  offset=1)

    def test_override_repo(self):
        override_repo('github.com/app/a', self.temp_specs_path)
        self.assertItemsEqual(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY),
                              {get_specs_repo().remote_path: self.temp_specs_path,
                               'github.com/app/a': self.temp_specs_path})

    def test_override_repo_colon(self):
        bad_path = os.path.join(self.temp_specs_path, 'colon:path')
        os.makedirs(bad_path)
        with self.assertRaises(RuntimeError):
            override_repo('github.com/app/a', bad_path)
        list_repos()
        self._assert_listed_repos(self.last_client_output,
                                  [['github.com/app/a', False],
                                   ['github.com/app/b', False]],
                                  offset=1)

    def test_override_then_manage_repo(self):
        override_repo('github.com/app/a', self.temp_specs_path)
        self.assertItemsEqual(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY),
                              {get_specs_repo().remote_path: self.temp_specs_path,
                               'github.com/app/a': self.temp_specs_path})
        manage_repo('github.com/app/a')
        self.assertItemsEqual(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY),
                              {get_specs_repo().remote_path: self.temp_specs_path})

    @patch('dusty.commands.repos._manage_repo')
    def test_override_then_manage_all(self, fake_manage_repo):
        override_repo('github.com/app/a', self.temp_specs_path)
        override_repo('github.com/app/b', self.temp_specs_path)
        manage_all_repos()
        fake_manage_repo.assert_has_calls([call('github.com/app/a'), call('github.com/app/b'),
                                           call(get_specs_repo().remote_path)], any_order=True)

    def test_override_repos_from_directory(self):
        override_repos_from_directory(self.temp_repos_path)
        self.assertItemsEqual(get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY),
                              {get_specs_repo().remote_path: self.temp_specs_path,
                               'github.com/app/a': os.path.join(self.temp_repos_path, 'a'),
                               'github.com/app/b': os.path.join(self.temp_repos_path, 'b'),
                               'github.com/lib/a': os.path.join(self.temp_repos_path, 'a')})

    @patch('dusty.source.Repo.update_local_repo')
    def test_update_managed_repos(self, fake_update_local_repo):
        activate_bundle(['bundle-a'])
        update_managed_repos()
        fake_update_local_repo.assert_has_calls([call()])

    @patch('dusty.source.Repo.update_local_repo')
    def test_update_managed_repos_for_both(self, fake_update_local_repo):
        activate_bundle(['bundle-a'])
        activate_bundle(['bundle-b'])
        update_managed_repos()
        fake_update_local_repo.assert_has_calls([call(), call()])
