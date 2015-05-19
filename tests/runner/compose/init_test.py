import os
import tempfile
import shutil

from unittest import TestCase
import yaml

from dusty import constants
from dusty.runner.compose import _write_composefile

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
