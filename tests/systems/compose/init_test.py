import os
import tempfile
import shutil

from mock import Mock, patch
import yaml

from dusty import constants
from dusty.systems.compose import (_write_composefile, _get_docker_env,
                                   _get_dusty_containers, _get_canonical_container_name)
from ...utils import DustyTestCase

class TestComposeSystem(DustyTestCase):
    def setUp(self):
        super(TestComposeSystem, self).setUp()
        self.temp_compose_dir = tempfile.mkdtemp()
        self.temp_compose_path = os.path.join(self.temp_compose_dir, 'docker-compose.yml')
        self.old_compose_dir = constants.COMPOSE_DIR
        constants.COMPOSE_DIR = self.temp_compose_dir
        self.test_spec = {'app-a': {'image': 'app/a'}}

        self.containers_return = [{'Names': ['/dusty_app-a_1']},
                                  {'Names': ['/dusty_app-b_1', '/dusty_app-a_1/dusty_app-b_1']}]
        self.fake_docker_client = Mock()
        self.fake_docker_client.containers.return_value = self.containers_return

    def tearDown(self):
        super(TestComposeSystem, self).tearDown()
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

    def test_get_dusty_containers_falsy(self):
        self.assertEqual(_get_dusty_containers(self.fake_docker_client, []),
                         self.containers_return)

    def test_get_dusty_containers_short_name(self):
        self.assertEqual(_get_dusty_containers(self.fake_docker_client, ['app-a']),
                         [self.containers_return[0]])

    def test_get_dusty_containers_long_name(self):
        self.assertEqual(_get_dusty_containers(self.fake_docker_client, ['app-b']),
                         [self.containers_return[1]])

    def test_get_canonical_container_name(self):
        self.assertEqual(_get_canonical_container_name(self.containers_return[1]), 'dusty_app-b_1')
