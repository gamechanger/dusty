from unittest import TestCase
from mock import patch, call

from dusty.commands.sync import sync_repos
from dusty.commands.bundles import activate_bundle
from ..utils import run, setup_test, teardown_test

class TestSyncCommand(TestCase):
    def setUp(self):
        setup_test(self)
        activate_bundle('bundle-a')
        activate_bundle('bundle-b')

    def tearDown(self):
        teardown_test(self)

    @patch('dusty.commands.sync.perform_sync_repos')
    def test_sync_repos_no_args(self, fake_sync):
        sync_repos()
        fake_sync.assert_has_calls([call(set(['github.com/app/a', 'github.com/app/b']))])

    @patch('dusty.commands.sync.perform_sync_repos')
    def test_sync_repos_with_one_arg(self, fake_sync):
        sync_repos('github.com/app/a')
        fake_sync.assert_has_calls([call(set(['github.com/app/a']))])

    @patch('dusty.commands.sync.perform_sync_repos')
    def test_sync_repos_with_multiple_args(self, fake_sync):
        sync_repos('github.com/app/a', 'github.com/app/b')
        fake_sync.assert_has_calls([call(set(['github.com/app/a', 'github.com/app/b']))])

    @patch('dusty.commands.sync.perform_sync_repos')
    def test_sync_repos_with_specs_repo(self, fake_sync):
        sync_repos('github.com/org/dusty-specs')
        fake_sync.assert_has_calls([call(set(['github.com/org/dusty-specs']))])
