import datetime
import dateutil.parser

from nose.tools import nottest

from dusty.compiler.spec_assembler import get_all_repos
from ...testcases import DustyIntegrationTestCase
from ...fixtures import specs_fixture_with_depends

class TestRestartCli(DustyIntegrationTestCase):
    def setUp(self):
        super(TestRestartCli, self).setUp()
        specs_fixture_with_depends()
        for repo in get_all_repos():
            self._set_up_fake_local_repo(path=repo.local_path)
        self.run_command('bundles activate bundle-a bundle-b')
        self.run_command('up')
        self.up_complete_time = datetime.datetime.now()

    def tearDown(self):
        try:
            self.run_command('stop')
        except Exception:
            pass
        super(TestStopCLI, self).tearDown()

    @nottest
    def container_has_restarted(self, app_name):
        inspected = self.inspect_container(app_name)
        start_time = dateutil.parser.parse(inspected['State']['StartedAt'])
        return start_time > self.up_complete_time

    def test_restart_one(self):
        self.run_command('restart app-a')
        self.assertTrue(self.container_has_restarted('app-a'))
        self.assertTrue(not self.container_has_restarted('app-b'))
        self.assertTrue(not self.container_has_restarted('app-c'))

    def test_restart_all(self):
        self.run_command('restart')
        self.assertTrue(self.container_has_restarted('app-a'))
        self.assertTrue(self.container_has_restarted('app-b'))
        self.assertTrue(self.container_has_restarted('app-c'))
