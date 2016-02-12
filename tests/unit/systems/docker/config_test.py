import os
import tempfile
import json

from dusty import constants
from dusty.systems.docker.config import registry_from_image, get_authed_registries
from ....testcases import DustyTestCase

class TestDockerConfigSystem(DustyTestCase):
    def setUp(self):
        super(TestDockerConfigSystem, self).setUp()
        self.temp_docker_config_path = tempfile.mkstemp()[1]
        self.old_docker_config_path = constants.DOCKER_CONFIG_PATH
        constants.DOCKER_CONFIG_PATH = self.temp_docker_config_path

    def tearDown(self):
        super(TestDockerConfigSystem, self).tearDown()
        constants.DOCKER_CONFIG_PATH = self.old_docker_config_path
        if os.path.exists(self.temp_docker_config_path):
            os.remove(self.temp_docker_config_path)

    def _write_config(self, config):
        json.dump(config, open(self.temp_docker_config_path, 'w'))

    def test_authed_registries_from_empty_config(self):
        os.remove(self.temp_docker_config_path)
        self.assertEqual(get_authed_registries(), set())

    def test_authed_registries_with_no_auth_key(self):
        self._write_config({'some_stuff': 'not auth'})
        self.assertEqual(get_authed_registries(), set())

    def test_authed_registries_with_https_auth(self):
        self._write_config({'auths': {'https://index.docker.io/v1/': {'stuff': 'irrelevant'}}})
        self.assertEqual(get_authed_registries(), set(['index.docker.io']))

    def test_authed_registries_with_multiple_styles(self):
        self._write_config({'auths': {'https://index.docker.io/v1/': {'stuff': 'irrelevant'},
                                      'gamechanger.io': {'stuff': 'irrelevant'}}})
        self.assertEqual(get_authed_registries(), set(['index.docker.io', 'gamechanger.io']))

    def test_registry_from_image_official(self):
        self.assertEqual(registry_from_image('postgres:9.3'),
                         'index.docker.io')

    def test_registry_from_image_public(self):
        self.assertEqual(registry_from_image('library/postgres:9.3'),
                         'index.docker.io')
        self.assertEqual(registry_from_image('thieman/clojure'),
                         'index.docker.io')

    def test_registry_from_image_private(self):
        self.assertEqual(registry_from_image('gamechanger.io/clojure:1.6'),
                         'gamechanger.io')
        self.assertEqual(registry_from_image('a.b.c.com/clojure:1.6'),
                         'a.b.c.com')
