from ...testcases import DustyIntegrationTestCase
from ...fixtures import specs_fixture_with_depends

class TestRestartCli(DustyIntegrationTestCase):
    def setUp(self):
        super(TestRestartCli, self).setUp()
        specs_fixture_with_depends()
        self.run_command('bundles activate bundle-a bundle-b')
