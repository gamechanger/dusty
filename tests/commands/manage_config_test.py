import os
import tempfile
import shutil

from unittest import TestCase

import dusty.constants
from dusty.config import write_default_config, save_config_value, get_config_value
from dusty.commands.manage_config import list_config, save_value
from ..fixtures import basic_specs_fixture

class TestManageConfigCommands(TestCase):
    def setUp(self):
        self.temp_config_path = tempfile.mkstemp()[1]
        self.temp_specs_path = tempfile.mkdtemp()
        self.old_config_path = dusty.constants.CONFIG_PATH
        dusty.constants.CONFIG_PATH = self.temp_config_path
        write_default_config()
        save_config_value('specs_path', self.temp_specs_path)
        basic_specs_fixture()
        self.expected_config = {'bundles': [], 'specs_path': self.temp_specs_path, 'repo_overrides': {}}

    def tearDown(self):
        os.remove(self.temp_config_path)
        shutil.rmtree(self.temp_specs_path)
        dusty.constants.CONFIG_PATH = self.old_config_path

    def test_list_config(self):
        result = list_config().next()
        self.assertEquals(result, self.expected_config)

    def test_set_value_changes_value_1(self):
        save_value('specs_path', '~/here').next()
        result = list_config().next()
        self.assertEquals(result, {'bundles': [], 'specs_path': '~/here', 'repo_overrides': {}})

    def test_set_value_changes_value_2(self):
        save_value('docker_user', '~/here').next()
        result = list_config().next()
        self.assertEquals(result, {'bundles': [], 'specs_path': self.temp_specs_path, 'repo_overrides': {}, 'docker_user': '~/here'})

    def test_set_value_no_changes_1(self):
        try:
            save_value('specs_pathers', '~/here').next()
        except:
            pass
        result = list_config().next()
        self.assertEquals(result, self.expected_config)

    def test_set_value_no_changes_2(self):
        try:
            save_value('bundles', '~/here').next()
        except:
            pass
        result = list_config().next()
        self.assertEquals(result, self.expected_config)
