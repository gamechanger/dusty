# coding=utf-8

import os
import tempfile
import shutil

from unittest import TestCase

import dusty.constants
from dusty.config import write_default_config, save_config_value, get_config_value
from dusty.commands.repos import list_repos, override_repo, manage_repo, override_repos_from_directory
from ..fixtures import basic_specs_fixture

class TestBundleCommands(TestCase):
    def setUp(self):
        self.temp_config_path = tempfile.mkstemp()[1]
        self.temp_specs_path = tempfile.mkdtemp()
        self.temp_repos_path = tempfile.mkdtemp()
        dusty.constants.CONFIG_PATH = self.temp_config_path
        write_default_config()
        save_config_value('specs_path', self.temp_specs_path)
        basic_specs_fixture()
        os.mkdir(os.path.join(self.temp_repos_path, 'a'))
        os.mkdir(os.path.join(self.temp_repos_path, 'b'))

    def tearDown(self):
        os.remove(self.temp_config_path)
        shutil.rmtree(self.temp_specs_path)
        shutil.rmtree(self.temp_repos_path)

    def _assert_listed_repos(self, result, repo_override_tuples):
        for index, repo_override in enumerate(repo_override_tuples):
            repo, override = repo_override
            output_row = index + 3
            self.assertIn(repo, result[output_row])
            if override:
                self.assertIn(override, result[output_row])

    def test_list_repos_with_no_overrides(self):
        result = list_repos().next().splitlines()
        self._assert_listed_repos(result, [['github.com/app/a', False],
                                           ['github.com/app/b', False]])

    def test_list_repos_with_one_override(self):
        override_repo('github.com/app/a', self.temp_specs_path).next()
        result = list_repos().next().splitlines()
        self._assert_listed_repos(result, [['github.com/app/a', self.temp_specs_path],
                                           ['github.com/app/b', False]])

    def test_list_repos_with_both_overridden(self):
        override_repo('github.com/app/a', self.temp_specs_path).next()
        override_repo('github.com/app/b', self.temp_specs_path).next()
        result = list_repos().next().splitlines()
        self._assert_listed_repos(result, [['github.com/app/a', self.temp_specs_path],
                                           ['github.com/app/b', self.temp_specs_path]])

    def test_override_repo(self):
        override_repo('github.com/app/a', self.temp_specs_path).next()
        self.assertItemsEqual(get_config_value('repo_overrides'), {'github.com/app/a': self.temp_specs_path})

    def test_deactivate_bundle(self):
        override_repo('github.com/app/a', self.temp_specs_path).next()
        self.assertItemsEqual(get_config_value('repo_overrides'), {'github.com/app/a': self.temp_specs_path})
        manage_repo('github.com/app/a').next()
        self.assertItemsEqual(get_config_value('repo_overrides'), {})

    def test_override_repos_from_directory(self):
        for result in override_repos_from_directory(self.temp_repos_path):
            pass
        self.assertItemsEqual(get_config_value('repo_overrides'), {'github.com/app/a': os.path.join(self.temp_repos_path, 'a'),
                                                                   'github.com/app/b': os.path.join(self.temp_repos_path, 'b')})
