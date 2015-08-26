import os

from dusty.source import Repo

from ...testcases import DustyIntegrationTestCase
from ...fixtures import single_specs_fixture

class TestEnvCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestEnvCLI, self).setUp()
        single_specs_fixture()
        local_dir = Repo('github.com/app/a').managed_path
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        self.run_command('bundles activate bundle-a')

    def tearDown(self):
        try:
            self.run_command('stop')
        except:
            pass
        self.run_command('env unset appa --all')
        super(TestEnvCLI, self).tearDown()

    def test_env_put_in_container(self):
        self.run_command('env set appa pitcher pedro')
        self.run_command('up --no-pull')
        self.assertEnvInContainer('appa', 'pitcher', 'pedro')

    def test_env_overrides_spec_environment(self):
        self.run_command('env set appa SPEC_VALUE new-value')
        self.run_command('up --no-pull')
        self.assertEnvInContainer('appa', 'SPEC_VALUE', 'new-value')
        self.assertEnvInContainer('appa', 'SPEC_VALUE2', 'spec-specified-value')

    def test_unset_all(self):
        self.run_command('env set appa pitcher pedro')
        self.run_command('env set appa SPEC_VALUE new-value')
        self.run_command('env unset appa --all')
        self.run_command('up --no-pull')
        self.assertEnvNotInContainer('appa', 'pitcher')
        self.assertEnvInContainer('appa', 'SPEC_VALUE', 'spec-specified-value')

    def test_unset_one(self):
        self.run_command('env set appa pitcher pedro')
        self.run_command('env set appa SPEC_VALUE new-value')
        self.run_command('env unset appa SPEC_VALUE')
        self.run_command('up --no-pull')
        self.assertEnvInContainer('appa', 'pitcher', 'pedro')
        self.assertEnvInContainer('appa', 'SPEC_VALUE', 'spec-specified-value')
