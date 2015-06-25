import datetime
import dateutil.parser

from nose.tools import nottest

from dusty.compiler.spec_assembler import get_all_repos
from ...testcases import DustyIntegrationTestCase
from ...fixtures import specs_fixture_with_depends

class TestRestartCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestRestartCLI, self).setUp()
        specs_fixture_with_depends()
        for repo in get_all_repos(include_specs_repo=False):
            print repo.remote_path
            self._set_up_fake_local_repo(path=repo.remote_path)
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
        self.run_command('restart appa')
        self.assertTrue(self.container_has_restarted('appa'))
        self.assertTrue(not self.container_has_restarted('appb'))
        self.assertTrue(not self.container_has_restarted('appc'))

    def test_restart_all(self):
        self.run_command('restart')
        self.assertTrue(self.container_has_restarted('appa'))
        self.assertTrue(self.container_has_restarted('appb'))
        self.assertTrue(self.container_has_restarted('appc'))

    def test_restart_by_app_repo(self):
        pass

    def test_restart_by_lib_repo(self):
        pass

    def test_restart_nosync(self):
        pass
