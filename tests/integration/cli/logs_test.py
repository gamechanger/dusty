from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestLogsCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestLogsCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)
        self.run_command('bundles activate busyboxa')
        self.run_command('up')

    def tearDown(self):
        try:
            self.run_command('stop')
        except Exception:
            pass
        super(TestLogsCLI, self).tearDown()

    def test_logs_on_running_container(self):
        self.run_command('logs busyboxa')
        self.assertExecDocker('logs', self.container_id('busyboxa'))

    def test_logs_on_stopped_container(self):
        self.run_command('stop')
        self.run_command('logs busyboxa')
        self.assertExecDocker('logs', self.container_id('busyboxa'))

    def test_logs_with_follow(self):
        self.run_command('logs -f busyboxa')
        self.assertExecDocker('logs', '-f', self.container_id('busyboxa'))

    def test_logs_with_lines(self):
        self.run_command('logs --tail=10 busyboxa')
        self.assertExecDocker('logs', '--tail=10', self.container_id('busyboxa'))

    def test_logs_with_timestamps(self):
        self.run_command('logs -t busyboxa')
        self.assertExecDocker('logs', '-t', self.container_id('busyboxa'))
