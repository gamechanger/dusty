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

    def test_managed_path_http(self):
        self.assertEqual(Repo('http://github.com/app/a').managed_path, '/etc/dusty/repos/github.com/app/a')

    def test_managed_path_file(self):
        self.assertEqual(Repo('file:///github.com/app/a').managed_path, '/etc/dusty/repos/github.com/app/a')

    def test_managed_path_ssh(self):
        self.assertEqual(Repo('ssh://git@github.com/app/a').managed_path, '/etc/dusty/repos/github.com/app/a')

    def test_rel_path(self):
        self.assertEqual(Repo('github.com/app/a').rel_path, 'github.com/app/a')
        self.assertEqual(Repo('github.com/app/a.js').rel_path, 'github.com/app/a.js')
        self.assertEqual(Repo('/gc/repos/dusty').rel_path, 'gc/repos/dusty')

    def test_rel_path_http(self):
        self.assertEqual(Repo('http://github.com/app/a').rel_path, 'github.com/app/a')

    def test_rel_path_file(self):
        self.assertEqual(Repo('file:///github.com/app/a.git').rel_path, 'github.com/app/a')
        self.assertEqual(Repo('file:///github.com/app/a.js.git').rel_path, 'github.com/app/a.js')

    def test_rel_path_ssh(self):
        self.assertEqual(Repo('ssh://git@github.com/app/a.git').rel_path, 'github.com/app/a')
        self.assertEqual(Repo('ssh://user@github.com:2222/app/a').rel_path, 'github.com/app/a')
        self.assertEqual(Repo('ssh://user@github.com:2222/app/a.js').rel_path, 'github.com/app/a.js')
        self.assertEqual(Repo('ssh://user@github.com:2222/app/a.js.git').rel_path, 'github.com/app/a.js')

    def test_override_path(self):
        override_repo('github.com/app/a', self.temp_dir)
        self.assertEqual(Repo('github.com/app/a').override_path, self.temp_dir)
        override_repo('/tmp/repo-c', self.temp_dir)
        self.assertEqual(Repo('/tmp/repo-c').override_path, self.temp_dir)

    def test_local_path(self):
        repo = Repo('github.com/app/a')
        self.assertEqual(repo.local_path, '/etc/dusty/repos/github.com/app/a')
        override_repo('github.com/app/a', self.temp_dir)
        self.assertEqual(repo.local_path, self.temp_dir)

    def test_vm_path(self):
        self.assertEqual(Repo('github.com/app/a').vm_path, '/dusty_repos/github.com/app/a')
        self.assertEqual(Repo('/tmp/repo-c').vm_path, '/dusty_repos/tmp/repo-c')

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
        self.MockableRepo('/tmp/repo-c').ensure_local_repo()
        fake_clone_from.assert_called_with('file:///tmp/repo-c', temp_dir)

    @patch('git.Repo.clone_from')
    def test_ensure_local_repo_when_does_not_exist_with_https_remote(self, fake_clone_from):
        temp_dir = os.path.join(self.temp_dir, 'd')
        self.MockableRepo.managed_path = property(lambda repo: temp_dir)
        self.MockableRepo('https://tmp/repo-c.git').ensure_local_repo()
        fake_clone_from.assert_called_with('https://tmp/repo-c.git', temp_dir)

    @patch('git.Repo.clone_from')
    def test_ensure_accepts_ssh_prefix_remote_path(self, fake_clone_from):
        temp_dir = os.path.join(self.temp_dir, 'd')
        self.MockableRepo.managed_path = property(lambda repo: temp_dir)
        self.MockableRepo('ssh://git@github.com/repos/c.git').ensure_local_repo()
        fake_clone_from.assert_called_with('ssh://git@github.com/repos/c.git', temp_dir)

    @patch('git.Repo.clone_from')
    def test_ensure_accepts_file_prefix_remote_path(self, fake_clone_from):
        temp_dir = os.path.join(self.temp_dir, 'd')
        self.MockableRepo.managed_path = property(lambda repo: temp_dir)
        self.MockableRepo('file:///tmp/repo-c.git').ensure_local_repo()
        fake_clone_from.assert_called_with('file:///tmp/repo-c.git', temp_dir)

    @patch('git.Repo.clone_from')
    def test_ensure_accepts_without_git_suffix(self, fake_clone_from):
        temp_dir = os.path.join(self.temp_dir, 'd')
        self.MockableRepo.managed_path = property(lambda repo: temp_dir)
        self.MockableRepo('https://tmp/repo-c').ensure_local_repo()
        fake_clone_from.assert_called_with('https://tmp/repo-c.git', temp_dir)

    @patch('git.Repo.clone_from')
    def test_ensure_local_repo_when_repo_exist(self, fake_clone_from):
        self.MockableRepo.managed_path = property(lambda repo: self.temp_dir)
        self.MockableRepo('github.com/app/a').ensure_local_repo()
        self.assertFalse(fake_clone_from.called)

    @patch('git.Repo')
    @patch('dusty.source.Repo.local_is_up_to_date')
    @patch('dusty.source.Repo.ensure_local_repo')
    def test_update_local_repo(self, fake_local_repo, fake_local_up_to_date, fake_repo):
        repo_mock = Mock()
        fake_local_up_to_date = Mock()
        pull_mock = Mock()
        repo_mock.remote.return_value = pull_mock
        fake_local_up_to_date.return_value = True
        fake_repo.return_value = repo_mock
        Repo('github.com/app/a').update_local_repo()
        pull_mock.pull.assert_called_once_with('master')

    def test_assemble_remote_path_1(self):
        repo_url = 'file:///path/to/repo'
        repo = Repo(repo_url)
        expected_url = 'file:///path/to/repo'

        self.assertEqual(repo.assemble_remote_path(), expected_url)

    def test_assemble_remote_path_2(self):
        repo_url = '/path/to/repo'
        repo = Repo(repo_url)
        expected_url = 'file:///path/to/repo'

        self.assertEqual(repo.assemble_remote_path(), expected_url)

    def test_assemble_remote_path_3(self):
        repo_url = 'http://path/to/repo.git'
        repo = Repo(repo_url)
        expected_url = 'http://path/to/repo.git'

        self.assertEqual(repo.assemble_remote_path(), expected_url)

    def test_assemble_remote_path_4(self):
        repo_url = 'http://path/to/repo'
        repo = Repo(repo_url)
        expected_url = 'http://path/to/repo.git'

        self.assertEqual(repo.assemble_remote_path(), expected_url)

    def test_assemble_remote_path_5(self):
        repo_url = 'ssh://path/to/repo/more_stuff'
        repo = Repo(repo_url)
        expected_url = 'ssh://path/to/repo/more_stuff'

        self.assertEqual(repo.assemble_remote_path(), expected_url)

    def test_assemble_remote_path_6(self):
        repo_url = 'ssh://path/to/repo:80/more_stuff'
        repo = Repo(repo_url)
        expected_url = 'ssh://path/to/repo:80/more_stuff'

        self.assertEqual(repo.assemble_remote_path(), expected_url)

    def test_assemble_remote_path_7(self):
        repo_url = 'git@path/to/repo:more_stuff'
        repo = Repo(repo_url)
        expected_url = 'git@path/to/repo:more_stuff'

        self.assertEqual(repo.assemble_remote_path(), expected_url)

    def test_assemble_remote_path_8(self):
        repo_url = 'path/to/repo'
        repo = Repo(repo_url)
        expected_url = 'ssh://git@path/to/repo'

        self.assertEqual(repo.assemble_remote_path(), expected_url)

