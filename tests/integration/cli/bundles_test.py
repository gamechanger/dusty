# coding=utf-8

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture

class TestBundlesCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestBundlesCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=2)

    def test_bundles_list_returns(self):
        result = self.run_command('bundles list')
        self.assertIn('busybox-a', result)
        self.assertIn('busybox-b', result)

    def test_bundles_activate(self):
        self.run_command('bundles activate busybox-a')
        result = self.run_command('bundles list')
        self.assertInSameLine(result, 'busybox-a', u'✓')
        self.assertNotInSameLine(result, 'busybox-b', u'✓')

    def test_bundles_activate_multiple(self):
        self.run_command('bundles activate busybox-a busybox-b')
        result = self.run_command('bundles list')
        self.assertInSameLine(result, 'busybox-a', u'✓')
        self.assertInSameLine(result, 'busybox-b', u'✓')

    def test_bundles_deactivate(self):
        self.run_command('bundles activate busybox-a')
        self.run_command('bundles deactivate busybox-a')
        result = self.run_command('bundles list')
        self.assertNotInSameLine(result, 'busybox-a', u'✓')
        self.assertNotInSameLine(result, 'busybox-b', u'✓')

    def test_bundles_deactivate_multiple(self):
        self.run_command('bundles activate busybox-b')
        self.run_command('bundles deactivate busybox-a busybox-b')
        result = self.run_command('bundles list')
        self.assertNotInSameLine(result, 'busybox-a', u'✓')
        self.assertNotInSameLine(result, 'busybox-b', u'✓')
