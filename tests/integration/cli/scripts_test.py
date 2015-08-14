from datetime import datetime
from os import path
from shutil import rmtree
from subprocess import check_call, check_output
from tempfile import mkdtemp
import time

import git
from mock import patch

from dusty import commands
from ...fixtures import single_specs_fixture
from ...testcases import DustyIntegrationTestCase

class TestScriptsCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestScriptsCLI, self).setUp()
        self.fake_repo_location = path.join(mkdtemp(), 'appa')
        self._set_up_fake_local_repo(path=self.fake_repo_location)
        single_specs_fixture()
        self.run_command('repos override github.com/app/a {}'.format(self.fake_repo_location))
        self.run_command('bundles activate bundle-a')
        self.run_command('up')

    def tearDown(self):
        try:
            self.run_command('stop --rm')
        except Exception:
            pass
        rmtree(self.fake_repo_location)
        super(TestScriptsCLI, self).tearDown()

    @DustyIntegrationTestCase.retriable_assertion(.1, 5)
    def assertFileInContainerRetriable(self, service_name, file_path):
        self.assertFileInContainer(service_name, file_path)

    @DustyIntegrationTestCase.retriable_assertion(.1, 5)
    def assertFileNotInContainerRetriable(self, service_name, file_path):
        self.assertFileNotInContainer(service_name, file_path)

    def test_basic(self):
        self.assertFileNotInContainer('appa', '/app/a/foo')
        self.run_command('scripts appa example')
        self.assertFileInContainerRetriable('appa', '/app/a/foo')
        self.exec_in_container('appa', 'rm /app/a/foo')

    def test_with_arg(self):
        self.run_command('scripts appa example')
        self.assertFileInContainerRetriable('appa', '/app/a/foo')
        self.run_command('scripts appa example_rm /app/a/foo')
        self.assertFileNotInContainerRetriable('appa', '/app/a/foo')

    def test_with_flag(self):
        self.run_command('scripts appa example_ls')
        self.run_command('scripts appa example_ls -l')
        self.assertTrue(len(self.exec_docker_processes[0].stdout.read()) < len(self.exec_docker_processes[1].stdout.read()))

    def test_with_flag_and_option(self):
        self.assertFileNotInContainer('appa', '/app/a/foo')
        self.run_command('scripts appa example_touch -c /app/a/foo')
        self.assertFileNotInContainer('appa', '/app/a/foo')
