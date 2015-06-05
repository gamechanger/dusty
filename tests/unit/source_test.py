import os
import tempfile
import shutil

import git
from mock import Mock, patch

from ..testcases import DustyTestCase
from dusty.commands.repos import override_repo
from dusty.source import Repo, git_error_handling
from dusty.compiler.spec_assembler import get_all_repos

class TestSource(DustyTestCase):
    def setUp(self):
        super(TestSource, self).setUp()
        self.temp_dir = tempfile.mkdtemp()

        self.MockableRepo = type("MockableRepo", (Repo, object), {})

    def tearDown(self):
        super(TestSource, self).tearDown()
        shutil.rmtree(self.temp_dir)

    def test_equality_true(self):
        self.assertEqual(Repo('github.com/app/a'), Repo('github.com/app/a'))

    def test_equality_false(self):
        self.assertNotEqual(Repo('github.com/app/a'), Repo('github.com/app/b'))

    def test_resolve_full_name(self):
        self.assertEqual(Repo.resolve(get_all_repos(), 'github.com/app/a'), Repo('github.com/app/a'))

    def test_resolve_short_name(self):
        self.assertEqual(Repo.resolve(get_all_repos(), 'b'), Repo('github.com/app/b'))

    def test_resolve_short_name_conflict(self):
        with self.assertRaises(RuntimeError):
            Repo.resolve(get_all_repos(), 'a')

    def test_resolve_not_found(self):
        with self.assertRaises(RuntimeError):
            Repo.resolve(get_all_repos(), 'definitely-not-a-repo')

    def test_is_local_repo(self):
        self.assertFalse(Repo('github.com/app/a').is_local_repo)
        self.assertTrue(Repo('/gc/repos/dusty').is_local_repo)

    def test_short_name_remote(self):
        self.assertEqual(Repo('github.com/app/a').short_name, 'a')

    def test_short_name_local(self):
        self.assertEqual(Repo('/gc/repos/dusty').short_name, 'dusty')

    def test_managed_path(self):
        self.assertEqual(Repo('github.com/app/a').managed_path, '/etc/dusty/repos/github.com/app/a')
        self.assertEqual(Repo('/gc/repos/dusty').managed_path, '/etc/dusty/repos/gc/repos/dusty')

    def test_override_path(self):
        override_repo('github.com/app/a', self.temp_dir)
        self.assertEqual(Repo('github.com/app/a').override_path, self.temp_dir)
        override_repo('/gc/repos/c', self.temp_dir)
        self.assertEqual(Repo('/gc/repos/c').override_path, self.temp_dir)

    def test_local_path(self):
        repo = Repo('github.com/app/a')
        self.assertEqual(repo.local_path, '/etc/dusty/repos/github.com/app/a')
        override_repo('github.com/app/a', self.temp_dir)
        self.assertEqual(repo.local_path, self.temp_dir)

    def test_vm_path(self):
        self.assertEqual(Repo('github.com/app/a').vm_path, '/persist/repos/github.com/app/a')
        self.assertEqual(Repo('/gc/repos/c').vm_path, '/persist/repos/gc/repos/c')

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
    def test_ensure_local_repo_when_does_not_exist_with_local_remote(self, fake_clone_from):
        temp_dir = os.path.join(self.temp_dir, 'c')
        self.MockableRepo.managed_path = property(lambda repo: temp_dir)
        self.MockableRepo('/gc/repos/c').ensure_local_repo()
        fake_clone_from.assert_called_with('file:////gc/repos/c', temp_dir)

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
