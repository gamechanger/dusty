# coding=utf-8

import os
import tempfile
import shutil

from unittest import TestCase

import dusty.constants
from dusty.config import write_default_config, save_config_value, get_config_value
from dusty.commands.bundle import list_bundles, activate_bundle, deactivate_bundle
from ..fixtures import basic_specs_fixture

class TestBundleCommands(TestCase):
    def setUp(self):
        self.temp_config_path = tempfile.mkstemp()[1]
        self.temp_specs_path = tempfile.mkdtemp()
        self.old_config_path = dusty.constants.CONFIG_PATH
        dusty.constants.CONFIG_PATH = self.temp_config_path
        write_default_config()
        save_config_value('specs_path', self.temp_specs_path)
        basic_specs_fixture()

    def tearDown(self):
        os.remove(self.temp_config_path)
        shutil.rmtree(self.temp_specs_path)
        dusty.constants.CONFIG_PATH = self.old_config_path

    def _assert_listed_bundles(self, result, bundle_active_tuples):
        for index, bundle_active in enumerate(bundle_active_tuples):
            bundle, activated = bundle_active
            output_row = index + 3
            self.assertIn(bundle, result[output_row])
            check_fn = self.assertIn if activated else self.assertNotIn
            check_fn(u"✓", result[output_row])

    def test_list_bundles_with_none_activated(self):
        result = list_bundles().next().splitlines()
        self._assert_listed_bundles(result, [['bundle-a', False],
                                             ['bundle-b', False]])

    def test_list_bundles_with_one_activated(self):
        activate_bundle('bundle-a').next()
        result = list_bundles().next().splitlines()
        self._assert_listed_bundles(result, [['bundle-a', True],
                                             ['bundle-b', False]])

    def test_list_bundles_with_both_activated(self):
        activate_bundle('bundle-a').next()
        activate_bundle('bundle-b').next()
        result = list_bundles().next().splitlines()
        self._assert_listed_bundles(result, [['bundle-a', True],
                                             ['bundle-b', True]])

    def test_activate_bundle(self):
        activate_bundle('bundle-a').next()
        self.assertItemsEqual(get_config_value('bundles'), ['bundle-a'])

    def test_deactivate_bundle(self):
        activate_bundle('bundle-a').next()
        self.assertItemsEqual(get_config_value('bundles'), ['bundle-a'])
        deactivate_bundle('bundle-a').next()
        self.assertItemsEqual(get_config_value('bundles'), [])
