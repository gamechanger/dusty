import os
import tempfile
import shutil

from unittest import TestCase
from mock import patch
import yaml

from dusty import constants
from dusty.systems.compose import _write_composefile, _get_docker_env

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

    @patch('dusty.demote.get_config_value')
    @patch('dusty.systems.compose.check_output_demoted')
    def test_get_docker_env(self, fake_check_output, fake_config_value):
        fake_config_value.return_value = 'root'
        fake_check_output.return_value = """    export DOCKER_TLS_VERIFY=1
        export DOCKER_HOST=tcp://192.168.59.103:2376
        export DOCKER_CERT_PATH=/Users/root/.boot2docker/certs/boot2docker-vm"""
        expected = {'DOCKER_TLS_VERIFY': '1',
                    'DOCKER_HOST': 'tcp://192.168.59.103:2376',
                    'DOCKER_CERT_PATH': '/Users/root/.boot2docker/certs/boot2docker-vm'}
        result = _get_docker_env()
        self.assertItemsEqual(result, expected)
