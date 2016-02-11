import os
import tempfile
import shutil

from dusty.config import get_config_value
from dusty.commands.bundles import list_bundles, activate_bundle, deactivate_bundle
from dusty.compiler.spec_assembler import get_specs_repo
from ...testcases import DustyTestCase
from dusty import constants

class TestBundlesCommands(DustyTestCase):
    def _assert_listed_bundles(self, result, bundle_active_tuples):
        for index, bundle_active in enumerate(bundle_active_tuples):
            bundle, activated = bundle_active
            output_row = index + 3
            self.assertIn(bundle, result.splitlines()[output_row])
            check_fn = self.assertIn if activated else self.assertNotIn
            check_fn("X", result.splitlines()[output_row])

    def test_list_bundles_with_none_activated(self):
        list_bundles()
        self._assert_listed_bundles(self.last_client_output,
                                    [['bundle-a', False],
                                     ['bundle-b', False]])

    def test_list_bundles_with_one_activated(self):
        activate_bundle(['bundle-a'], False)
        list_bundles()
        self._assert_listed_bundles(self.last_client_output,
                                    [['bundle-a', True],
                                     ['bundle-b', False]])

    def test_list_bundles_with_both_activated(self):
        activate_bundle(['bundle-a', 'bundle-b'], False)
        list_bundles()
        self._assert_listed_bundles(self.last_client_output,
                                    [['bundle-a', True],
                                     ['bundle-b', True]])

    def test_activate_bundle(self):
        activate_bundle(['bundle-a'], False)
        self.assertItemsEqual(get_config_value(constants.CONFIG_BUNDLES_KEY), ['bundle-a'])

    def test_activate_bundle_only(self):
        activate_bundle(['bundle-a'], False)
        activate_bundle(['bundle-b'], True)
        self.assertItemsEqual(get_config_value(constants.CONFIG_BUNDLES_KEY), ['bundle-b'])

    def test_deactivate_bundle(self):
        activate_bundle(['bundle-a', 'bundle-b'], False)
        self.assertItemsEqual(get_config_value(constants.CONFIG_BUNDLES_KEY), ['bundle-a', 'bundle-b'])
        deactivate_bundle(['bundle-a', 'bundle-b'])
        self.assertItemsEqual(get_config_value(constants.CONFIG_BUNDLES_KEY), [])
