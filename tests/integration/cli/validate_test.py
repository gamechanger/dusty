import shutil
import tempfile

from schemer import ValidationException
from dusty.compiler.spec_assembler import get_specs_path

from ...testcases import DustyIntegrationTestCase
from ...fixtures import busybox_single_app_bundle_fixture, invalid_fixture

class TestValidateCLI(DustyIntegrationTestCase):
    def setUp(self):
        super(TestValidateCLI, self).setUp()
        busybox_single_app_bundle_fixture(num_bundles=1)
        # Set up a location we know we can write to but put nothing there
        # because shutil.copytree demands the dest be empty
        self.temp_dir = tempfile.mkdtemp()
        shutil.rmtree(self.temp_dir)

    def tearDown(self):
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
        super(TestValidateCLI, self).tearDown()

    def test_validate_success(self):
        self.run_command('validate')

    def test_validate_failure(self):
        invalid_fixture()
        # This raises a CommandError because the daemon does the validation
        with self.assertRaises(self.CommandError):
            self.run_command('validate')

    def test_validate_success_against_location(self):
        shutil.copytree(get_specs_path(), self.temp_dir)
        self.run_command('validate {}'.format(self.temp_dir))

    def test_validate_failure_against_location(self):
        invalid_fixture()
        shutil.copytree(get_specs_path(), self.temp_dir)
        # Here, the client does the validation, so we instead get a
        # ValidationException directly from schemer
        with self.assertRaises(ValidationException):
            self.run_command('validate {}'.format(self.temp_dir))
