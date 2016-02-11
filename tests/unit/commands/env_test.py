import os
import tempfile

from dusty.commands import env
from dusty.commands.bundles import activate_bundle

from ...testcases import DustyTestCase

class TestEnvCommands(DustyTestCase):
    def setUp(self):
        super(TestEnvCommands, self).setUp()
        activate_bundle(['bundle-a', 'bundle-b'], False)
        self.temp_file = tempfile.mkstemp()[1]

    def tearDown(self):
        super(TestEnvCommands, self).tearDown()
        os.remove(self.temp_file)

    def assertEnvNotListed(self, app_or_service, variable):
        env.list_all()
        for line in self.last_client_output.splitlines():
            self.assertFalse(app_or_service in line and variable in line)

    def assertEnvListed(self, app_or_service, variable, value):
        env.list_all()
        print self.last_client_output.splitlines()
        self.assertTrue(any([app_or_service in line and variable in line and value in line
            for line in self.last_client_output.splitlines()]))

    def test_list_all(self):
        env.set_var('app-a', 'dad', 'homer')
        env.set_var('app-a', 'mom', 'marge')
        env.set_var('app-b', 'evil', 'cmb')
        self.assertEnvListed('app-a', 'dad', 'homer')
        self.assertEnvListed('app-a', 'mom', 'marge')
        self.assertEnvListed('app-b', 'evil', 'cmb')

    def test_list_app_or_service(self):
        env.set_var('app-a', 'mom', 'marge')
        env.set_var('app-b', 'evil', 'cmb')
        env.list_app_or_service('app-a')
        self.assertTrue('mom' in self.last_client_output and 'marge' in self.last_client_output)
        self.assertFalse('evil' in self.last_client_output or 'cmb' in self.last_client_output)
        env.list_app_or_service('app-b')
        self.assertTrue('evil' in self.last_client_output and 'cmb' in self.last_client_output)
        self.assertFalse('marge' in self.last_client_output)

    def test_set_var(self):
        self.assertEnvNotListed('app-a', 'vehicle')
        env.set_var('app-a', 'vehicle', 'train')
        self.assertEnvListed('app-a', 'vehicle', 'train')
        self.assertEnvNotListed('app-b', 'vehicle')

    def test_set_file(self):
        with open(self.temp_file, 'w') as f:
            f.write('bart=simpson\n')
            f.write('lisa=simpson\n')
        env.set_from_file('app-a', self.temp_file)
        self.assertEnvListed('app-a', 'bart', 'simpson')
        self.assertEnvListed('app-a', 'lisa', 'simpson')

    def test_unset_all(self):
        env.set_var('app-a', 'pitcher', 'pedro')
        env.set_var('app-a', 'batter', 'arod')
        env.set_var('app-b', 'set', 'appb')
        env.unset_all('app-a')
        self.assertEnvListed('app-b', 'set', 'appb')
        self.assertEnvNotListed('app-a', 'pitcher')
        self.assertEnvNotListed('app-a', 'batter')

    def test_unset_var(self):
        env.set_var('app-a', 'pitcher', 'pedro')
        env.set_var('app-a', 'batter', 'arod')
        env.set_var('app-b', 'set', 'appb')
        env.unset_var('app-a', 'batter')
        self.assertEnvListed('app-b', 'set', 'appb')
        self.assertEnvListed('app-a', 'pitcher', 'pedro')
        self.assertEnvNotListed('app-a', 'batter')
