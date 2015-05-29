from mock import patch

from ..utils import DustyTestCase
from dusty.payload import Payload
from dusty.commands.cp import copy_between_containers, copy_from_local, copy_to_local
from dusty.cli.cp import _split_path, main

class TestCpCLI(DustyTestCase):
    def test_split_path_no_name(self):
        self.assertEqual(_split_path('/tmp/path.txt'), (None, '/tmp/path.txt'))

    def test_split_path_with_name(self):
        self.assertEqual(_split_path('website:/tmp/path.txt'), ('website', '/tmp/path.txt'))

    def test_split_too_many_colons(self):
        with self.assertRaises(ValueError):
            _split_path('website:api:/tmp/path.txt')

    def test_main_local_to_container(self):
        result = main(['/tmp/a', 'website:/tmp/b'])
        self.assertEqual(result, Payload(copy_from_local, '/tmp/a', 'website', '/tmp/b'))

    def test_main_container_to_local(self):
        result = main(['website:/tmp/a', '/tmp/b'])
        self.assertEqual(result, Payload(copy_to_local, '/tmp/b', 'website', '/tmp/a'))

    def test_main_container_to_container(self):
        result = main(['website:/tmp/a', 'api:/tmp/b'])
        self.assertEqual(result, Payload(copy_between_containers, 'website', '/tmp/a', 'api', '/tmp/b'))

    def test_main_fails_on_local_copy(self):
        with self.assertRaises(ValueError):
            main(['/tmp/a', '/tmp/b'])
