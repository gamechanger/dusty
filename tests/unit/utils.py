import os
import shutil
import tempfile
import logging

from unittest import TestCase
from nose.tools import nottest

import dusty.constants
from dusty.config import write_default_config, save_config_value
from dusty.compiler.spec_assembler import get_specs_repo
from dusty.commands.repos import override_repo
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
