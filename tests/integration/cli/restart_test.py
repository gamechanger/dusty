import datetime
import dateutil.parser

from nose.tools import nottest

from ...testcases import DustyIntegrationTestCase
from ...fixtures import specs_fixture_with_depends

class TestRestartCli(DustyIntegrationTestCase):
    def setUp(self):
        super(TestRestartCli, self).setUp()
        specs_fixture_with_depends()
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
