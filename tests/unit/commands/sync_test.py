from mock import patch, call

from dusty.commands.sync import sync_repos
from dusty.commands.bundles import activate_bundle
from dusty.source import Repo
from ...testcases import DustyTestCase

class TestSyncCommand(DustyTestCase):
    def setUp(self):
        super(TestSyncCommand, self).setUp()
        activate_bundle(['bundle-a'])
        activate_bundle(['bundle-b'])

    @patch('dusty.commands.sync.perform_sync_repos')
    def test_sync_repos_no_args(self, fake_sync):
        sync_repos()
        fake_sync.assert_has_calls([call(set([Repo('github.com/app/a'), Repo('github.com/app/b')]))])

    @patch('dusty.commands.sync.perform_sync_repos')
    def test_sync_repos_with_one_arg(self, fake_sync):
        sync_repos('github.com/app/a')
        fake_sync.assert_has_calls([call(set([Repo('github.com/app/a')]))])

    @patch('dusty.commands.sync.perform_sync_repos')
    def test_sync_repos_with_multiple_args(self, fake_sync):
        sync_repos('github.com/app/a', 'github.com/app/b')
        fake_sync.assert_has_calls([call(set([Repo('github.com/app/a'), Repo('github.com/app/b')]))])

    @patch('dusty.commands.sync.perform_sync_repos')
    def test_sync_repos_with_multiple_args_short_name(self, fake_sync):
        sync_repos('a', 'b')
        fake_sync.assert_has_calls([call(set([Repo('github.com/app/a'), Repo('github.com/app/b')]))])
