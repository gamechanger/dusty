import os
import tempfile
import shutil
import textwrap

from unittest import TestCase
from mock import patch
import yaml

from dusty import constants
from dusty.systems.compose import _write_composefile, _get_docker_env, _dusty_shared_folder_already_exists

class TestComposeRunner(TestCase):
    def setUp(self):
        self.temp_compose_dir = tempfile.mkdtemp()
        self.temp_compose_path = os.path.join(self.temp_compose_dir, 'docker-compose.yml')
        self.old_compose_dir = constants.COMPOSE_DIR
        constants.COMPOSE_DIR = self.temp_compose_dir
        self.test_spec = {'app-a': {'image': 'app/a'}}

    def tearDown(self):
        constants.COMPOSE_DIR = self.old_compose_dir
        shutil.rmtree(self.temp_compose_dir)

    def test_write_composefile(self):
        _write_composefile(self.test_spec)
        written = open(self.temp_compose_path, 'r').read()
        self.assertItemsEqual(yaml.load(written), self.test_spec)

    @patch('dusty.systems.compose._check_output_demoted')
    def test_get_docker_env(self, fake_check_output):
        fake_check_output.return_value = """    export DOCKER_TLS_VERIFY=1
        export DOCKER_HOST=tcp://192.168.59.103:2376
        export DOCKER_CERT_PATH=/Users/root/.boot2docker/certs/boot2docker-vm"""
        expected = {'DOCKER_TLS_VERIFY': '1',
                    'DOCKER_HOST': 'tcp://192.168.59.103:2376',
                    'DOCKER_CERT_PATH': '/Users/root/.boot2docker/certs/boot2docker-vm'}
        result = _get_docker_env()
        self.assertItemsEqual(result, expected)

    @patch('dusty.systems.compose._check_output_demoted')
    def test_dusty_shared_folder_already_exists_false(self, fake_check_output):
        fake_check_output.return_value = textwrap.dedent("""\
        vrde="off"
        usb="off"
        ehci="off"
        SharedFolderNameMachineMapping1="Users"
        SharedFolderPathMachineMapping1="/Users"
        """)
        self.assertFalse(_dusty_shared_folder_already_exists())

    @patch('dusty.systems.compose._check_output_demoted')
    def test_dusty_shared_folder_already_exists_true(self, fake_check_output):
        fake_check_output.return_value = textwrap.dedent("""\
        vrde="off"
        usb="off"
        ehci="off"
        SharedFolderNameMachineMapping1="dusty"
        SharedFolderPathMachineMapping1="/etc/dusty"
        """)
        self.assertTrue(_dusty_shared_folder_already_exists())
