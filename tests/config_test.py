import os
import tempfile

from .utils import DustyTestCase
from dusty import constants, config

class TestConfig(DustyTestCase):
    def setUp(self):
        super(TestConfig, self).setUp()
        self.test_config = {'bundles': ['bundle-a'], 'repo_overrides': {'repo-a': '/var/run/repo-a'}, 'mac_username': 'root'}

    def test_save_and_get_config(self):
        config.save_config(self.test_config)
        self.assertItemsEqual(self.test_config, config.get_config())

    def test_get_config_value(self):
        config.save_config(self.test_config)
        self.assertItemsEqual(config.get_config_value('bundles'), ['bundle-a'])
        self.assertItemsEqual(config.get_config_value('repo_overrides'), {'repo-a': '/var/run/repo-a'})
        self.assertEqual(config.get_config_value('mac_username'), 'root')

    def test_save_config_value(self):
        config.save_config(self.test_config)
        self.assertItemsEqual(config.get_config_value('bundles'), ['bundle-a'])
        config.save_config_value('bundles', ['bundle-b'])
        self.assertItemsEqual(config.get_config_value('bundles'), ['bundle-b'])
        config.save_config_value('new_key', 'bacon')
        self.assertEqual(config.get_config_value('new_key'), 'bacon')

    def test_assert_config_key(self):
        config.save_config(self.test_config)
        config.assert_config_key('mac_username')
        with self.assertRaises(KeyError):
            config.assert_config_key('nonexistent_key')
