import os
import tempfile
import shutil
import json

import dusty.constants
from dusty.commands.manage_config import list_config_values, save_value, _eligible_config_keys_for_setting
from dusty.compiler.spec_assembler import get_specs_repo
from ..utils import DustyTestCase

class TestManageConfigCommands(DustyTestCase):
    def setUp(self):
        super(TestManageConfigCommands, self).setUp()
        self.old_config_path = dusty.constants.CONFIG_PATH
        dusty.constants.CONFIG_SETTINGS = {k: '' for k in ['bundles', 'repo_overrides', 'specs_repo', 'docker_user']}
        self.expected_config = {'bundles': [],
                                'repo_overrides': {get_specs_repo(): self.temp_specs_path},
                                'specs_repo': 'github.com/org/dusty-specs',
                                'nginx_includes_dir': '/usr/local/etc/nginx/servers'}

    def tearDown(self):
        super(TestManageConfigCommands, self).tearDown()
        dusty.constants.CONFIG_PATH = self.old_config_path

    def test_eligible_config_key_for_setting(self):
        self.assertItemsEqual(_eligible_config_keys_for_setting(), ['specs_repo', 'docker_user'])

    def test_list_config_values(self):
        list_config_values()
        self.assertItemsEqual(json.loads(self.last_client_output.replace('\'', '\"')), self.expected_config)

    def test_save_value_changes_value(self):
        save_value('docker_user', '~/here')
        list_config_values()
        self.assertItemsEqual(json.loads(self.last_client_output.replace('\'', '\"')),
                              {'bundles': [],
                               'repo_overrides': {get_specs_repo(): self.temp_specs_path},
                               'docker_user': '~/here',
                               'specs_repo': 'github.com/org/dusty-specs',
                               'nginx_includes_dir': '/usr/local/etc/nginx/servers'})

    def test_save_value_no_changes(self):
        with self.assertRaises(KeyError):
            save_value('bundles', '~/here')
