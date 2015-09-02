import os
import tempfile
import shutil

from mock import Mock, patch
import yaml

from dusty import constants
from dusty.systems.docker import (get_docker_env, get_dusty_containers, get_dusty_images, get_container_for_app_or_service,
                                  get_canonical_container_name, exec_in_container)

from dusty.systems.docker.compose import write_composefile
from dusty.systems.docker.cleanup import get_exited_dusty_containers
from dusty.compiler.spec_assembler import get_specs
from ....testcases import DustyTestCase

class TestComposeSystem(DustyTestCase):
    def setUp(self):
        super(TestComposeSystem, self).setUp()
        self.temp_compose_dir = tempfile.mkdtemp()
        self.temp_compose_path = os.path.join(self.temp_compose_dir, 'docker-compose.yml')
        self.old_compose_dir = constants.COMPOSE_DIR
        self.old_compose_path = constants.COMPOSEFILE_PATH
        constants.COMPOSE_DIR = self.temp_compose_dir
        constants.COMPOSEFILE_PATH = self.temp_compose_path
        self.test_spec = {'app-a': {'image': 'app/a'}}

        self.containers_return = [{'Names': ['/dusty_app-a_1'], 'Status': 'Exited'},
                                  {'Names': ['/dusty_app-b_1', '/dusty_app-a_1/dusty_app-b_1'], 'Status': 'Running'},
                                  {'Names': ['/some-random-image']}]
        self.fake_docker_client = Mock()
        self.fake_docker_client.containers.return_value = self.containers_return

    def tearDown(self):
        super(TestComposeSystem, self).tearDown()
        constants.COMPOSE_DIR = self.old_compose_dir
        constants.COMPOSEFILE_PATH = self.old_compose_path
        shutil.rmtree(self.temp_compose_dir)

    def testwrite_composefile(self):
        write_composefile(self.test_spec, constants.COMPOSEFILE_PATH)
        written = open(self.temp_compose_path, 'r').read()
        self.assertItemsEqual(yaml.load(written), self.test_spec)

    @patch('dusty.subprocess.get_config_value')
    @patch('dusty.systems.docker.check_output_demoted')
    def test_get_docker_env_1(self, fake_check_output, fake_config_value):
        fake_config_value.return_value = 'root'
        fake_check_output.return_value = """    export DOCKER_TLS_VERIFY=1
        export DOCKER_HOST=tcp://192.168.59.103:2376
        export DOCKER_CERT_PATH=/Users/root/.docker/machine/machines/dusty/cert.pem"""
        expected = {'DOCKER_TLS_VERIFY': '1',
                    'DOCKER_HOST': 'tcp://192.168.59.103:2376',
                    'DOCKER_CERT_PATH': '/Users/root/.docker/machine/machines/dusty/cert.pem'}
        result = get_docker_env()
        self.assertItemsEqual(result, expected)

    @patch('dusty.subprocess.get_config_value')
    @patch('dusty.systems.docker.check_output_demoted')
    @patch('dusty.systems.docker.os.environ', {'DOCKER_TLS_VERIFY': '2',
                                               'DOCKER_HOST': 'tcp://192.168.59.103:2375',
                                               'DOCKER_CERT_PATH': 'baaaaaad'})
    def test_get_docker_env_2(self, fake_check_output, fake_config_value):
        fake_config_value.return_value = 'root'
        fake_check_output.return_value = """    export DOCKER_TLS_VERIFY=1
        export DOCKER_HOST=tcp://192.168.59.103:2376
        export DOCKER_CERT_PATH=/Users/root/.docker/machine/machines/dusty/cert.pem"""
        expected = {'DOCKER_TLS_VERIFY': '1',
                    'DOCKER_HOST': 'tcp://192.168.59.103:2376',
                    'DOCKER_CERT_PATH': '/Users/root/.docker/machine/machines/dusty/cert.pem'}
        result = get_docker_env()
        self.assertItemsEqual(result, expected)

    @patch('dusty.systems.docker.get_docker_client')
    def test_get_dusty_containers_falsy(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        self.assertEqual(get_dusty_containers([]), self.containers_return[:-1])

    @patch('dusty.systems.docker.get_docker_client')
    def test_get_dusty_containers_short_name(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        self.assertEqual(get_dusty_containers(['app-a']), [self.containers_return[0]])

    @patch('dusty.systems.docker.get_docker_client')
    def test_get_dusty_containers_long_name(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        self.assertEqual(get_dusty_containers(['app-b']), [self.containers_return[1]])

    def test_get_canonical_container_name(self):
        self.assertEqual(get_canonical_container_name(self.containers_return[1]), 'dusty_app-b_1')

    @patch('dusty.systems.docker.get_docker_client')
    def test_get_exited_containers(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        self.assertEqual(get_exited_dusty_containers(), [self.containers_return[0]])

    def test_get_dusty_images(self):
        self.assertEqual(get_dusty_images(), set(['app/a:latest', 'app/b:latest', 'app/c:latest', 'service/a:latest']))

    @patch('dusty.systems.docker.get_docker_client')
    def test_get_container_for_app_or_service(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        result = get_container_for_app_or_service('app-a')
        self.assertIn('/dusty_app-a_1', result['Names'])

    @patch('dusty.systems.docker.get_docker_client')
    def test_get_container_for_app_or_service_none_found(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        result = get_container_for_app_or_service('app-c')
        self.assertIsNone(result)

    @patch('dusty.systems.docker.get_docker_client')
    def test_get_container_for_app_or_service_none_found_with_raise(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        with self.assertRaises(RuntimeError):
            get_container_for_app_or_service('app-c', raise_if_not_found=True)

    @patch('dusty.systems.docker.get_docker_client')
    def test_exec_in_container_with_args(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        self.fake_docker_client.exec_create.return_value = {'Id': 'exec-id'}
        fake_container = {'Id': 'container-id'}
        exec_in_container(fake_container, 'cp -r', '/tmp/a', '/tmp/b')
        self.fake_docker_client.exec_create.assert_called_once_with('container-id', 'cp -r /tmp/a /tmp/b')

    @patch('dusty.systems.docker.get_docker_client')
    def test_exec_in_container_without_args(self, patch_docker_client):
        patch_docker_client.return_value = self.fake_docker_client
        self.fake_docker_client.exec_create.return_value = {'Id': 'exec-id'}
        fake_container = {'Id': 'container-id'}
        exec_in_container(fake_container, 'ls')
        self.fake_docker_client.exec_create.assert_called_once_with('container-id', 'ls')
