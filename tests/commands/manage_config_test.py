import os
import tempfile
import shutil

from unittest import TestCase

import dusty.constants
from dusty.commands.manage_config import list_config_values, save_value, _eligible_config_keys_for_setting
from dusty.compiler.spec_assembler import get_specs_repo
from ..utils import setup_test, teardown_test

class TestManageConfigCommands(TestCase):
    def setUp(self):
        setup_test(self)
        self.old_config_path = dusty.constants.CONFIG_PATH
        dusty.constants.CONFIG_SETTINGS = {k: '' for k in ['bundles', 'repo_overrides', 'specs_repo', 'docker_user']}
        self.expected_config = {'bundles': [], 'repo_overrides': {get_specs_repo(): self.temp_specs_path}, 'specs_repo': 'github.com/org/dusty-specs'}

    def tearDown(self):
        teardown_test(self)
        dusty.constants.CONFIG_PATH = self.old_config_path

    def test_eligible_config_key_for_setting(self):
        self.assertItemsEqual(_eligible_config_keys_for_setting(), ['specs_repo', 'docker_user'])

    def test_list_config_values(self):
        result = list_config_values().next()
        self.assertEquals(result, self.expected_config)

    def test_save_value_changes_value(self):
        save_value('docker_user', '~/here').next()
        result = list_config_values().next()
        self.assertEquals(result, {'bundles': [], 'repo_overrides': {get_specs_repo(): self.temp_specs_path}, 'docker_user': '~/here', 'specs_repo': 'github.com/org/dusty-specs'})

    def test_save_value_no_changes(self):
        with self.assertRaises(KeyError):
            save_value('bundles', '~/here').next()

    def test_save_value_no_arguemnts(self):
        result = save_value().next()
        self.assertEquals(result, "Call with arguments `key value`, where key is in {}".format(['docker_user', 'specs_repo']))

    def test_save_value_one_argument(self):
        with self.assertRaises(ValueError):
            save_value('specs_repo').next()
