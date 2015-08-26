import os
import tempfile
import time

from dusty.systems.virtualbox import asset_is_set, _run_command_on_vm
from dusty import constants
from dusty.source import Repo
from dusty.memoize import reset_memoize_cache
from ...testcases import DustyIntegrationTestCase
from ...fixtures import assets_fixture

class TestAssetsCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestAssetsCLI, self).setUp()
        assets_fixture()

        local_dir = Repo('github.com/lib/a').managed_path
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        self.required_app_file = tempfile.mkstemp()[1]
        with open(self.required_app_file, 'w') as f:
            f.write('required_app_contents')
        self.optional_app_file = tempfile.mkstemp()[1]
        with open(self.optional_app_file, 'w') as f:
            f.write('optional_app_contents')
        self.required_lib_file = tempfile.mkstemp()[1]
        with open(self.required_lib_file, 'w') as f:
            f.write('required_lib_contents')
        self.optional_lib_file = tempfile.mkstemp()[1]
        with open(self.optional_lib_file, 'w') as f:
            f.write('optional_lib_contents')

        self.run_command('bundles activate bundle-a')
        self.run_command('assets set required_app_asset {}'.format(self.required_app_file))
        self.run_command('assets set required_lib_asset {}'.format(self.required_lib_file))

    def tearDown(self):
        os.remove(self.required_app_file)
        os.remove(self.required_lib_file)
        os.remove(self.optional_app_file)
        os.remove(self.optional_lib_file)

        _run_command_on_vm('sudo rm -rf {}'.format(constants.VM_ASSETS_DIR))
        try:
            self.run_command('stop --rm')
        except:
            pass
        super(TestAssetsCLI, self).tearDown()

    @DustyIntegrationTestCase.retriable_assertion(.1, 5)
    def assertAssetContentsRetriable(self, container_path, asset_contents):
        self.assertFileContentsInContainer('app-a', container_path, asset_contents)

    def test_asset_in_container(self):
        self.run_command('up --no-pull')
        self.assertAssetContentsRetriable('/required_app_path', 'required_app_contents')
        self.assertAssetContentsRetriable('/required_lib_path', 'required_lib_contents')

    def test_required_asset_fail(self):
        self.run_command('bundles activate bundle-a')
        self.run_command('assets unset required_app_asset')
        with self.assertRaises(self.CommandError):
            output = self.run_command('up --no-pull')

    def test_optional_asset(self):
        self.run_command('assets set optional_app_asset {}'.format(self.optional_app_file))
        self.run_command('assets set optional_lib_asset {}'.format(self.optional_lib_file))
        self.run_command('up --no-pull')
        self.assertAssetContentsRetriable('/optional_app_path', 'optional_app_contents')
        self.assertAssetContentsRetriable('/optional_lib_path', 'optional_lib_contents')


    def test_unset(self):
        self.run_command('assets unset required_app_asset')
        self.run_command('assets unset required_lib_asset')
        reset_memoize_cache()
        self.assertFalse(asset_is_set('required_app_asset'))
        self.assertFalse(asset_is_set('required_lib_asset'))

    def test_read(self):
        with self.assertLogToClientOutput('required_app_contents'):
            self.run_command('assets read required_app_asset')
        with self.assertLogToClientOutput('required_lib_contents'):
            self.run_command('assets read required_lib_asset')
