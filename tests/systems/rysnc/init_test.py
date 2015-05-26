from unittest import TestCase
from mock import patch, call

from ...utils import setup_test, teardown_test
from dusty.systems.rsync import sync_repos_by_app_or_service_name

class TestRysnc(TestCase):
    def setUp(self):
        setup_test(self)

    def tearDown(self):
        teardown_test(self)

    @patch('dusty.systems.rsync.sync_repos')
    def test_sync_repos_by_app_or_service_name(self, fake_sync_repos):
        sync_repos_by_app_or_service_name(['app-a', 'app-b', 'lib-a'])
        fake_sync_repos.assert_has_calls([call(['github.com/app/a', 'github.com/app/b', 'github.com/lib/a'])])
