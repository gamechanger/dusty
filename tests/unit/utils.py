import os
import sys
import shutil
import tempfile
import logging

from unittest import TestCase
from nose.tools import nottest
from mock import patch

import dusty.constants
from dusty.config import write_default_config, save_config_value
from dusty.compiler.spec_assembler import get_specs_repo
from dusty.commands.repos import override_repo
from dusty.cli import main as client_entrypoint
from .fixtures import basic_specs_fixture

class TestCaptureHandler(logging.Handler):
    def __init__(self, lst):
        super(TestCaptureHandler, self).__init__()
        self.lst = lst

    def emit(self, record):
        self.lst.append(self.format(record))

class DustyTestCase(TestCase):
    def setUp(self):
        self.temp_config_path = tempfile.mkstemp()[1]
        self.temp_specs_path = tempfile.mkdtemp()
        self.temp_repos_path = tempfile.mkdtemp()

        dusty.constants.CONFIG_PATH = self.temp_config_path
        write_default_config()
        save_config_value(dusty.constants.CONFIG_SPECS_REPO_KEY, 'github.com/org/dusty-specs')
        override_repo(get_specs_repo(), self.temp_specs_path)
        basic_specs_fixture()

        self.client_output = []
        self.capture_handler = TestCaptureHandler(self.client_output)
        logging.getLogger(dusty.constants.SOCKET_LOGGER_NAME).addHandler(self.capture_handler)

    def tearDown(self):
        os.remove(self.temp_config_path)
        shutil.rmtree(self.temp_specs_path)
        shutil.rmtree(self.temp_repos_path)
        logging.getLogger(dusty.constants.SOCKET_LOGGER_NAME).removeHandler(self.capture_handler)

    @property
    def last_client_output(self):
        return self.client_output[-1] if self.client_output else None

class DustyIntegrationTestCase(TestCase):
    """This test case intentionally avoids mocking whenever possible
    in order to get as close as possible to the actual state that
    would be experienced on a system running Dusty. Therefore,
    integration tests are possibly destructive if run on a user's
    machine. To help protect the user from running them accidentally,
    integration tests will refuse to run unless the environment
    variable DUSTY_ALLOW_INTEGRATION_TESTS is set.

    Note that this also assumes it is running against an actual
    Dustyd process on the local host."""
    def setUp(self):
        if not os.getenv('DUSTY_ALLOW_INTEGRATION_TESTS'):
            raise RuntimeError('You must set the env var DUSTY_ALLOW_INTEGRATION_TESTS to run integration tests. '
                               'This may affect your local config, do not run integration tests on your actual '
                               "machine unless you know what you're doing!")
        self.overridden_specs_path = tempfile.mkdtemp()
        write_default_config()
        save_config_value('specs_repo', 'github.com/gamechanger/example-dusty-specs')
        override_repo(get_specs_repo(), self.overridden_specs_path)

    def tearDown(self):
        shutil.rmtree(self.overridden_specs_path)

    @property
    def stdout(self):
        return sys.stdout.getvalue().strip()

    @patch('sys.exit')
    def run_command(self, args, fake_exit):
        sys.argv = ['dusty'] + args.split(' ')
        client_entrypoint()

    def _in_same_line(self, *values):
        for line in self.stdout.splitlines():
            if all(value in line for value in values):
                return True
        return False

    def assertInSameLine(self, *values):
        self.assertTrue(self._in_same_line(*values))

    def assertNotInSameLine(self, *values):
        self.assertFalse(self._in_same_line(*values))