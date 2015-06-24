import time

from nose.tools import nottest

from ...testcases import DustyIntegrationTestCase
from ...fixtures import specs_fixture_with_depends

class TestRestartCli(DustyIntegrationTestCase):
    def setUp(self):
        super(TestRestartCli, self).setUp()
        specs_fixture_with_depends()
        self.run_command('bundles activate bundle-a bundle-b')
        self.run_command('up')
        self.up_complete_time = time.time()

    def tearDown(self):
        try:
            self.run_command('stop')
        except Exception:
            pass
        super(TestStopCLI, self).tearDown()

    @nottest
    def container_has_restarted(app_name, up_complete_time):
        inspected = self.inspect_container(app_name)
