import datetime
import os
import time

import dateutil.parser
from nose.tools import nottest

from dusty.compiler.spec_assembler import get_all_repos
from dusty.source import Repo
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
        self.up_complete_time = datetime.datetime.utcnow()

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

    def test_restart_nosync(self):
        new_file_name = 'nosync_file'
        repo = Repo.resolve(get_all_repos(include_specs_repo=False), 'repo-app-a')
        with open(os.path.join(repo.local_path, new_file_name), 'w+') as f:
            f.write('new file!')
        self.run_command('restart --no-sync appa')
        self.assertFileNotInContainer('appa', os.path.join('/app/a/', new_file_name))

    def test_restart_sync(self):
        new_file_name = 'sync_file'
        repo = Repo.resolve(get_all_repos(include_specs_repo=False), 'app-a')
        with open(os.path.join(repo.local_path, new_file_name), 'w+') as f:
            f.write('new file!')
        self.run_command('restart appa')
        self.assertFileInContainer('appa', os.path.join('/app/a/', new_file_name))
