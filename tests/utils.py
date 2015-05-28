import os
import shutil
import tempfile
import logging

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

@nottest
def setup_test(obj):
    obj.temp_config_path = tempfile.mkstemp()[1]
    obj.temp_specs_path = tempfile.mkdtemp()
    obj.temp_repos_path = tempfile.mkdtemp()
    dusty.constants.CONFIG_PATH = obj.temp_config_path
    write_default_config()
    save_config_value('specs_repo', 'github.com/org/dusty-specs')
    override_repo(get_specs_repo(), obj.temp_specs_path)
    basic_specs_fixture()
    obj.client_output = []
    obj.capture_handler = TestCaptureHandler(obj.client_output)
    logging.getLogger(dusty.constants.SOCKET_LOGGER_NAME).addHandler(obj.capture_handler)

@nottest
def teardown_test(obj):
    os.remove(obj.temp_config_path)
    shutil.rmtree(obj.temp_specs_path)
    shutil.rmtree(obj.temp_repos_path)
    logging.getLogger(dusty.constants.SOCKET_LOGGER_NAME).removeHandler(obj.capture_handler)
