# coding=utf-8

import sys

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_fixture

class TestBundlesCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestBundlesCLI, self).setUp()
        busybox_single_app_fixture(num_bundles=2)

    def test_bundles_list_returns(self):
        self.run_command('bundles list')
        self.assertIn('busybox-a', self.stdout)
        self.assertIn('busybox-b', self.stdout)

    def test_bundles_activate(self):
        self.run_command('bundles activate busybox-a')
        self.run_command('bundles list')
        self.assertInSameLine('busybox-a', u'✓')
        self.assertNotInSameLine('busybox-b', u'✓')

    def test_bundles_activate_multiple(self):
        self.run_command('bundles activate busybox-a busybox-b')
        self.run_command('bundles list')
        self.assertInSameLine('busybox-a', u'✓')
        self.assertInSameLine('busybox-b', u'✓')

    def test_bundles_deactivate(self):
        self.run_command('bundles activate busybox-a')
        self.run_command('bundles deactivate busybox-a')
        self.run_command('bundles list')
        self.assertNotInSameLine('busybox-a', u'✓')
        self.assertNotInSameLine('busybox-b', u'✓')

    def test_bundles_deactivate_multiple(self):
        self.run_command('bundles activate busybox-b')
        self.run_command('bundles deactivate busybox-a busybox-b')
        self.run_command('bundles list')
        self.assertNotInSameLine('busybox-a', u'✓')
        self.assertNotInSameLine('busybox-b', u'✓')
