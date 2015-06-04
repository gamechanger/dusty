import os

from mock import patch

from ...testcases import DustyTestCase
from dusty.payload import Payload
from dusty.commands.cp import copy_between_containers, copy_from_local, copy_to_local
from dusty.cli.cp import _split_path, _resolve_path, _validate_path_pair, main

class TestCpCLI(DustyTestCase):
    def test_split_path_no_name(self):
        self.assertEqual(_split_path('/tmp/path.txt'), (None, '/tmp/path.txt'))

    def test_split_path_with_name(self):
        self.assertEqual(_split_path('website:/tmp/path.txt'), ('website', '/tmp/path.txt'))

    def test_split_too_many_colons(self):
        with self.assertRaises(ValueError):
            _split_path('website:api:/tmp/path.txt')

    def test_resolve_path_absolute(self):
        self.assertEqual(_resolve_path('/tmp/a'), '/tmp/a')

    def test_resolve_path_relative(self):
        self.assertEqual(_resolve_path('a'), os.path.join(os.getcwd(), 'a'))

    def test_validate_path_pair_success_local_absolute(self):
        _validate_path_pair(None, '/tmp/a')

    def test_validate_path_pair_success_local_relative(self):
        _validate_path_pair(None, 'a')

    def test_validate_path_pair_success_container(self):
        _validate_path_pair('some-container', '/tmp/a')

    def test_validate_path_pair_relative_in_container(self):
        with self.assertRaises(RuntimeError):
            _validate_path_pair('some-container', 'a')

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
