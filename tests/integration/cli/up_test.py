import subprocess

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture
from dusty.systems.docker import get_docker_env

class TestUpCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestUpCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=2)
        self.run_command('bundles activate busyboxa busyboxb')

    def test_basic_up_command(self):
        run_output = self.run_command('up')
        self.assertTrue('Your local environment is now started!' in run_output)

        docker_output = subprocess.check_output(['sh', '-c', "docker ps"], env=get_docker_env())
        self.assertTrue('dusty_busyboxa_1' in docker_output)
        self.assertTrue('dusty_busyboxb_1' in docker_output)

    def test_basic_up_recreate(self):
        run_output = self.run_command('up')
        run_output = self.run_command('up')
        self.assertTrue('Recreating dusty_busyboxb_1' in run_output)
        self.assertTrue('Recreating dusty_busyboxa_1' in run_output)
        run_output = self.run_command('up --no-recreate')
        self.assertFalse('Recreating dusty_busyboxb_1' in run_output)
        self.assertFalse('Recreating dusty_busyboxa_1' in run_output)

    def test_basic_up_no_pull(self):
        run_output = self.run_command('up')
        self.assertTrue('Updating managed copy of /tmp/fake-repo' in run_output)
        run_output = self.run_command('up --no-pull')
        self.assertFalse('Updating managed copy of /tmp/fake-repo' in run_output)
