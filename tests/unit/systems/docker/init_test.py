import os
import tempfile
import shutil

from mock import Mock, patch
import yaml

from dusty import constants
from dusty.systems.docker import (get_docker_env, _get_dusty_containers, get_dusty_images, _get_container_for_app_or_service,
                                  _get_canonical_container_name, _exec_in_container)

from dusty.systems.docker.compose import _write_composefile
from dusty.systems.docker.cleanup import _get_exited_dusty_containers
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
        # self.fake_docker_client.

    def tearDown(self):
        super(TestComposeSystem, self).tearDown()
        constants.COMPOSE_DIR = self.old_compose_dir
        constants.COMPOSEFILE_PATH = self.old_compose_path
        shutil.rmtree(self.temp_compose_dir)

    def test_write_composefile(self):
        _write_composefile(self.test_spec)
        written = open(self.temp_compose_path, 'r').read()
        self.assertItemsEqual(yaml.load(written), self.test_spec)

    @patch('dusty.demote.get_config_value')
    @patch('dusty.systems.docker.check_output_demoted')
    def testget_docker_env(self, fake_check_output, fake_config_value):
        fake_config_value.return_value = 'root'
        fake_check_output.return_value = """    export DOCKER_TLS_VERIFY=1
        export DOCKER_HOST=tcp://192.168.59.103:2376
        export DOCKER_CERT_PATH=/Users/root/.boot2docker/certs/boot2docker-vm"""
        expected = {'DOCKER_TLS_VERIFY': '1',
                    'DOCKER_HOST': 'tcp://192.168.59.103:2376',
                    'DOCKER_CERT_PATH': '/Users/root/.boot2docker/certs/boot2docker-vm'}
        result = get_docker_env()
        self.assertItemsEqual(result, expected)

    def test_get_dusty_containers_falsy(self):
        self.assertEqual(_get_dusty_containers(self.fake_docker_client, []),
                         self.containers_return[:-1])

    def test_get_dusty_containers_short_name(self):
        self.assertEqual(_get_dusty_containers(self.fake_docker_client, ['app-a']),
                         [self.containers_return[0]])

    def test_get_dusty_containers_long_name(self):
        self.assertEqual(_get_dusty_containers(self.fake_docker_client, ['app-b']),
                         [self.containers_return[1]])

    def test_get_canonical_container_name(self):
        self.assertEqual(_get_canonical_container_name(self.containers_return[1]), 'dusty_app-b_1')

    def test_get_exited_containers(self):
        self.assertEqual(_get_exited_dusty_containers(self.fake_docker_client), [self.containers_return[0]])

    def test_get_dusty_images(self):
        self.assertEqual(get_dusty_images(), set(['app/a:latest', 'app/b:latest', 'app/c:latest', 'service/a:latest']))

    def test_get_container_for_app_or_service(self):
        result = _get_container_for_app_or_service(self.fake_docker_client, 'app-a')
        self.assertIn('/dusty_app-a_1', result['Names'])

    def test_get_container_for_app_or_service_none_found(self):
        result = _get_container_for_app_or_service(self.fake_docker_client, 'app-c')
        self.assertIsNone(result)

    def test_get_container_for_app_or_service_none_found_with_raise(self):
        with self.assertRaises(RuntimeError):
            _get_container_for_app_or_service(self.fake_docker_client,
                                              'app-c',
                                              raise_if_not_found=True)

    def test_exec_in_container_with_args(self):
        self.fake_docker_client.exec_create.return_value = {'Id': 'exec-id'}
        fake_container = {'Id': 'container-id'}
        _exec_in_container(self.fake_docker_client, fake_container, 'cp -r', '/tmp/a', '/tmp/b')
        self.fake_docker_client.exec_create.assert_called_once_with('container-id', 'cp -r /tmp/a /tmp/b')

    def test_exec_in_container_without_args(self):
        self.fake_docker_client.exec_create.return_value = {'Id': 'exec-id'}
        fake_container = {'Id': 'container-id'}
        _exec_in_container(self.fake_docker_client, fake_container, 'ls')
        self.fake_docker_client.exec_create.assert_called_once_with('container-id', 'ls')
