# -*- coding: utf-8 -*-

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture, unicode_fixture

class TestBundlesCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestBundlesCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=2)

    def test_bundles_list_returns(self):
        result = self.run_command('bundles list')
        self.assertIn('busyboxa', result)
        self.assertIn('busyboxb', result)

    def test_bundles_activate(self):
        self.run_command('bundles activate busyboxa')
        result = self.run_command('bundles list')
        self.assertInSameLine(result, 'busyboxa', 'X')
        self.assertNotInSameLine(result, 'busyboxb', 'X')

    def test_bundles_activate_multiple(self):
        self.run_command('bundles activate busyboxa busyboxb')
        result = self.run_command('bundles list')
        self.assertInSameLine(result, 'busyboxa', 'X')
        self.assertInSameLine(result, 'busyboxb', 'X')

    def test_bundles_activate_only(self):
        self.run_command('bundles activate busyboxa')
        self.run_command('bundles activate --only busyboxb')
        result = self.run_command('bundles list')
        self.assertNotInSameLine(result, 'busyboxa', 'X')
        self.assertInSameLine(result, 'busyboxb', 'X')

    def test_bundles_deactivate(self):
        self.run_command('bundles activate busyboxa')
        self.run_command('bundles deactivate busyboxa')
        result = self.run_command('bundles list')
        self.assertNotInSameLine(result, 'busyboxa', 'X')
        self.assertNotInSameLine(result, 'busyboxb', 'X')

    def test_bundles_deactivate_multiple(self):
        self.run_command('bundles activate busyboxb')
        self.run_command('bundles deactivate busyboxa busyboxb')
        result = self.run_command('bundles list')
        self.assertNotInSameLine(result, 'busyboxa', 'X')
        self.assertNotInSameLine(result, 'busyboxb', 'X')

    def test_bundles_with_unicode_names(self):
        unicode_fixture()
        self.run_command('bundles activate bundle-Ɯ')
        result = self.run_command('bundles list')
        self.assertInSameLine(result, 'bundle-Ɯ', 'X', 'unicode woohoooၕഇഞƺ')
