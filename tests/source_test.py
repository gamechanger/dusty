import os
import tempfile
import shutil

import git
from unittest import TestCase
from mock import Mock, patch

from .utils import setup_test, teardown_test
from dusty.commands.repos import override_repo
from dusty.source import (repo_is_overridden, local_repo_path, _short_repo_name,
                          git_error_handling, ensure_local_repo, update_local_repo)

class TestSource(TestCase):
    def setUp(self):
        setup_test(self)
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        teardown_test(self)
        shutil.rmtree(self.temp_dir)

    def test_repo_is_overridden_true(self):
        override_repo('github.com/app/a', self.temp_dir)
        self.assertTrue(repo_is_overridden('github.com/app/a'))

    def test_repo_is_overridden_false(self):
        self.assertFalse(repo_is_overridden('github.com/app/a'))

    def test_local_repo_path_no_override(self):
        self.assertEqual(local_repo_path('github.com/app/a'),
                         '/etc/dusty/repos/github.com/app/a')

    def test_local_repo_path_with_override(self):
        override_repo('github.com/app/a', self.temp_dir)
        self.assertEqual(local_repo_path('github.com/app/a'), self.temp_dir)

    def test_short_repo_name(self):
        self.assertEqual(_short_repo_name('github.com/app/a'), 'a')

    @patch('dusty.source.log_to_client')
    def test_git_error_handling(self, fake_log_to_client):
        with self.assertRaises(git.exc.GitCommandError):
            with git_error_handling():
                raise git.exc.GitCommandError('cmd', 'status')
        self.assertTrue(fake_log_to_client.called)

    @patch('git.Repo.clone_from')
    @patch('dusty.source._managed_repo_path')
    def test_ensure_local_repo_when_does_not_exist(self, fake_repo_path, fake_clone_from):
        temp_dir = os.path.join(self.temp_dir, 'a')
        fake_repo_path.return_value = temp_dir
        ensure_local_repo('github.com/app/a')
        fake_clone_from.assert_called_with('ssh://git@github.com/app/a', temp_dir)

    @patch('git.Repo.clone_from')
    @patch('dusty.source._managed_repo_path')
    def test_ensure_local_repo_when_repo_exist(self, fake_repo_path, fake_clone_from):
        fake_repo_path.return_value = self.temp_dir
        ensure_local_repo('github.com/app/a')
        self.assertFalse(fake_clone_from.called)

    @patch('git.Repo')
    @patch('dusty.source.ensure_local_repo')
    def test_update_local_repo(self, fake_local_repo, fake_repo):
        repo_mock = Mock()
        pull_mock = Mock()
        repo_mock.remote.return_value = pull_mock
        fake_repo.return_value = repo_mock
        update_local_repo('github.com/app/a')
        pull_mock.pull.assert_called_once_with('master')
