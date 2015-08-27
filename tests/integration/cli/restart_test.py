import datetime
import os
from subprocess import check_call
from tempfile import mkdtemp
import time

import dateutil.parser
from nose.tools import nottest

from dusty.compiler.spec_assembler import get_all_repos
from dusty import constants
from dusty.source import Repo
from dusty.subprocess import check_output_demoted
from ...testcases import DustyIntegrationTestCase
from ...fixtures import specs_fixture_with_depends

class TestRestartCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestRestartCLI, self).setUp()
        specs_fixture_with_depends()
        for repo in get_all_repos(include_specs_repo=False):
            self._set_up_fake_local_repo(path=repo.remote_path)
        self.run_command('bundles activate bundle-a bundle-b')
        self.run_command('up')
        time.sleep(.1)
        # VM time and host time may deviate so we need to take our benchmark
        # of when setUp has completed from the VM
        self.up_complete_time = self.vm_current_time()

    def tearDown(self):
        try:
            self.run_command('stop')
        except Exception:
            pass
        super(TestRestartCLI, self).tearDown()

    def assertContainerHasRestarted(self, app_name):
        self.assertTrue(self.container_has_restarted(app_name))

    def assertContainerNotRestarted(self, app_name):
        self.assertFalse(self.container_has_restarted(app_name))

    def vm_current_time(self):
        result = check_output_demoted(['docker-machine', 'ssh', constants.VM_MACHINE_NAME, 'date "+%Y-%m-%dT%X.%s"'])
        return dateutil.parser.parse(result)

    @nottest
    def container_has_restarted(self, app_name):
        inspected = self.inspect_container(app_name)
        start_time = dateutil.parser.parse(inspected['State']['StartedAt']).replace(tzinfo=None)
        return start_time > self.up_complete_time

    def test_restart_one(self):
        self.run_command('restart appa')
        self.assertContainerHasRestarted('appa')
        self.assertContainerNotRestarted('appb')
        self.assertContainerNotRestarted('appc')

    def test_restart_all(self):
        self.run_command('restart')
        self.assertContainerHasRestarted('appa')
        self.assertContainerHasRestarted('appb')
        self.assertContainerHasRestarted('appc')

    def test_restart_by_app_repo(self):
        self.run_command('restart --repos repo-app-a')
        self.assertContainerHasRestarted('appa')
        self.assertContainerNotRestarted('appb')
        self.assertContainerNotRestarted('appc')

    def test_restart_by_lib_repo(self):
        self.run_command('restart --repos repo-lib-a')
        self.assertContainerHasRestarted('appa')
        self.assertContainerHasRestarted('appb')
        self.assertContainerNotRestarted('appc')

    def test_restart_sync(self):
        new_file_name = 'sync_file'
        repo = Repo.resolve(get_all_repos(include_specs_repo=False), 'repo-app-a')
        with open(os.path.join(repo.local_path, new_file_name), 'w+') as f:
            f.write('new file!')
        self.run_command('restart appa')
        self.assertFileInContainer('appa', os.path.join('/app/a/', new_file_name))

    def test_restart_dead_container(self):
        self.run_command('stop appa')
        self.run_command('restart appa')
        self.assertContainerHasRestarted('appa')

    def test_restart_fails_with_dead_link(self):
        self.run_command('stop appa')
        output = self.run_command('restart appb')
        self.assertInSameLine(output, 'Cannot restart appb', 'appa')

    def test_restart_with_repo_swap(self):
        repo_override_dir = mkdtemp()
        extra_file = 'train'
        extra_file_path = os.path.join(repo_override_dir, extra_file)
        check_call(['touch', extra_file_path])
        self.run_command('repos override repo-app-a {}'.format(repo_override_dir))
        self.run_command('restart appa')
        extra_file_container_path = os.path.join('/app/a', extra_file)
        self.assertFileInContainer('appa', extra_file_container_path)
