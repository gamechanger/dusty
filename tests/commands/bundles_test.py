# coding=utf-8

import os
import tempfile
import shutil

from unittest import TestCase

from dusty.config import get_config_value
from dusty.commands.bundles import list_bundles, activate_bundle, deactivate_bundle
from dusty.compiler.spec_assembler import get_specs_repo
from ..utils import setup_test, teardown_test

class TestBundlesCommands(TestCase):
    def setUp(self):
        setup_test(self)

    def tearDown(self):
        teardown_test(self)

    def _assert_listed_bundles(self, result, bundle_active_tuples):
        for index, bundle_active in enumerate(bundle_active_tuples):
            bundle, activated = bundle_active
            output_row = index + 3
            self.assertIn(bundle, result.splitlines()[output_row])
            check_fn = self.assertIn if activated else self.assertNotIn
            check_fn(u"✓", result.splitlines()[output_row])

    def test_list_bundles_with_none_activated(self):
        list_bundles()
        self._assert_listed_bundles(self.client_output[-1],
                                    [['bundle-a', False],
                                     ['bundle-b', False]])

    def test_list_bundles_with_one_activated(self):
        activate_bundle('bundle-a')
        list_bundles()
        self._assert_listed_bundles(self.client_output[-1],
                                    [['bundle-a', True],
                                     ['bundle-b', False]])

    def test_list_bundles_with_both_activated(self):
        activate_bundle('bundle-a')
        activate_bundle('bundle-b')
        list_bundles()
        self._assert_listed_bundles(self.client_output[-1],
                                    [['bundle-a', True],
                                     ['bundle-b', True]])

    def test_activate_bundle(self):
        activate_bundle('bundle-a')
        self.assertItemsEqual(get_config_value('bundles'), ['bundle-a'])

    def test_deactivate_bundle(self):
        activate_bundle('bundle-a')
        self.assertItemsEqual(get_config_value('bundles'), ['bundle-a'])
        deactivate_bundle('bundle-a')
        self.assertItemsEqual(get_config_value('bundles'), [])
