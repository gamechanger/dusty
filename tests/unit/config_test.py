import os
import tempfile

from ..testcases import DustyTestCase
from dusty import constants, config

class TestConfig(DustyTestCase):
    def setUp(self):
        super(TestConfig, self).setUp()
        self.test_config = {constants.CONFIG_BUNDLES_KEY: ['bundle-a'], constants.CONFIG_REPO_OVERRIDES_KEY: {'repo-a': '/var/run/repo-a'}, constants.CONFIG_MAC_USERNAME_KEY: 'root'}

    def test_save_and_get_config(self):
        config.save_config(self.test_config)
        self.assertItemsEqual(self.test_config, config.get_config())

    def test_get_config_value(self):
        config.save_config(self.test_config)
        self.assertItemsEqual(config.get_config_value(constants.CONFIG_BUNDLES_KEY), ['bundle-a'])
        self.assertItemsEqual(config.get_config_value(constants.CONFIG_REPO_OVERRIDES_KEY), {'repo-a': '/var/run/repo-a'})
        self.assertEqual(config.get_config_value(constants.CONFIG_MAC_USERNAME_KEY), 'root')

    def test_save_config_value(self):
        config.save_config(self.test_config)
        self.assertItemsEqual(config.get_config_value(constants.CONFIG_BUNDLES_KEY), ['bundle-a'])
        config.save_config_value(constants.CONFIG_BUNDLES_KEY, ['bundle-b'])
        self.assertItemsEqual(config.get_config_value(constants.CONFIG_BUNDLES_KEY), ['bundle-b'])
        config.save_config_value('new_key', 'bacon')
        self.assertEqual(config.get_config_value('new_key'), 'bacon')
