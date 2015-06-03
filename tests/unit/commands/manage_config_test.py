import os
import tempfile
import shutil
import json

import dusty.constants
from dusty.commands.manage_config import list_config_values, save_value, _eligible_config_keys_for_setting
from dusty.compiler.spec_assembler import get_specs_repo
from ..utils import DustyTestCase
from dusty import constants

class TestManageConfigCommands(DustyTestCase):
    def setUp(self):
        super(TestManageConfigCommands, self).setUp()
        self.old_config_path = dusty.constants.CONFIG_PATH
        self.old_config_settings = dusty.constants.CONFIG_SETTINGS
        dusty.constants.CONFIG_SETTINGS = {k: '' for k in [constants.CONFIG_BUNDLES_KEY, constants.CONFIG_REPO_OVERRIDES_KEY, constants.CONFIG_SPECS_REPO_KEY, 'docker_user']}
        self.expected_config = {constants.CONFIG_BUNDLES_KEY: [],
                                constants.CONFIG_REPO_OVERRIDES_KEY: {get_specs_repo(): self.temp_specs_path},
                                constants.CONFIG_SPECS_REPO_KEY: 'github.com/org/dusty-specs',
                                constants.CONFIG_NGINX_DIR_KEY: '/usr/local/etc/nginx/servers',
                                constants.CONFIG_SETUP_KEY: False}

    def tearDown(self):
        super(TestManageConfigCommands, self).tearDown()
        dusty.constants.CONFIG_PATH = self.old_config_path
        dusty.constants.CONFIG_SETTINGS = self.old_config_settings

    def test_eligible_config_key_for_setting(self):
        self.assertItemsEqual(_eligible_config_keys_for_setting(), [constants.CONFIG_SPECS_REPO_KEY, 'docker_user'])

    def test_list_config_values(self):
        list_config_values()
        self.assertItemsEqual(json.loads(self.last_client_output.replace('\'', '\"').replace('False', 'false').replace('True', 'true')), self.expected_config)

    def test_save_value_changes_value(self):
        save_value('docker_user', '~/here')
        list_config_values()
        self.assertItemsEqual(json.loads(self.last_client_output.replace('\'', '\"').replace('False', 'false').replace('True', 'true')),
                              {constants.CONFIG_BUNDLES_KEY: [],
                               constants.CONFIG_REPO_OVERRIDES_KEY: {get_specs_repo(): self.temp_specs_path},
                               'docker_user': '~/here',
                               constants.CONFIG_SPECS_REPO_KEY: 'github.com/org/dusty-specs',
                               constants.CONFIG_NGINX_DIR_KEY: '/usr/local/etc/nginx/servers',
                               constants.CONFIG_SETUP_KEY: False})

    def test_save_value_no_changes(self):
        with self.assertRaises(KeyError):
            save_value(constants.CONFIG_BUNDLES_KEY, '~/here')
