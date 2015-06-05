import os
import tempfile
import shutil

import git
from mock import Mock, patch

from ..testcases import DustyTestCase
from dusty.commands.repos import override_repo
from dusty.source import Repo, git_error_handling

class TestSource(DustyTestCase):
    def setUp(self):
        super(TestSource, self).setUp()
        self.temp_dir = tempfile.mkdtemp()

        self.MockableRepo = type("MockableRepo", (Repo, object), {})

    def tearDown(self):
        super(TestSource, self).tearDown()
        shutil.rmtree(self.temp_dir)

    def test_repo_is_overridden_true(self):
        override_repo('github.com/app/a', self.temp_dir)
        self.assertTrue(Repo('github.com/app/a').is_overridden)

    def test_repo_is_overridden_false(self):
        self.assertFalse(Repo('github.com/app/a').is_overridden)

    def test_short_repo_name(self):
        self.assertEqual(Repo('github.com/app/a').short_name, 'a')

    @patch('dusty.source.log_to_client')
    def test_git_error_handling(self, fake_log_to_client):
        with self.assertRaises(git.exc.GitCommandError):
            with git_error_handling():
                raise git.exc.GitCommandError('cmd', 'status')
        self.assertTrue(fake_log_to_client.called)

    @patch('git.Repo.clone_from')
    def test_ensure_local_repo_when_does_not_exist(self, fake_clone_from):
        temp_dir = os.path.join(self.temp_dir, 'a')
        self.MockableRepo.managed_path = property(lambda repo: temp_dir)
        self.MockableRepo('github.com/app/a').ensure_local_repo()
        fake_clone_from.assert_called_with('ssh://git@github.com/app/a', temp_dir)

    @patch('git.Repo.clone_from')
    def test_ensure_local_repo_when_repo_exist(self, fake_clone_from):
        self.MockableRepo.managed_path = property(lambda repo: self.temp_dir)
        self.MockableRepo('github.com/app/a').ensure_local_repo()
        self.assertFalse(fake_clone_from.called)

    @patch('git.Repo')
    @patch('dusty.source.Repo.ensure_local_repo')
    def test_update_local_repo(self, fake_local_repo, fake_repo):
        repo_mock = Mock()
        pull_mock = Mock()
        repo_mock.remote.return_value = pull_mock
        fake_repo.return_value = repo_mock
        Repo('github.com/app/a').update_local_repo()
        pull_mock.pull.assert_called_once_with('master')
