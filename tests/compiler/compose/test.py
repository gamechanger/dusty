from unittest import TestCase
from mock import patch

from dusty import constants
from dusty.compiler.compose import (get_compose_dict, _composed_app_dict, _composed_service_dict,
                                    _get_ports_list, _compile_docker_command, _get_compose_volumes)
from ..test_test_cases import all_test_configs


def repo_path(name):
    return "/Users/gc/{}".format(name.split('/')[-1])

@patch('dusty.compiler.compose.repo_path', side_effect=repo_path)
class TestComposeCompiler(TestCase):
    def test_composed_volumes(self, *args):
        specs = {
            'apps': {
                'app1': {
                    'repo': '/cool/repo/app1',
                    'depends': {
                        'libs': ['lib1', 'lib2']
                    }
                }
            },
            'libs': {
                'lib1': {
                    'repo': '/cool/repo/lib1',
                },
                'lib2': {
                    'repo': '/cool/repo/lib2',
                },
                'lib3': {
                    'repo': '/cool/repo/lib3',
                }
            }
        }
        expected_volumes = [
            '/Users/gc/app1:/gc/app1',
            '/Users/gc/lib1:/gc/lib1',
            '/Users/gc/lib2:/gc/lib2'
        ]
        returned_volumes = _get_compose_volumes('app1', specs)
        self.assertEqual(expected_volumes, returned_volumes)

    def test_compile_command_with_once(self, *args):
        app_spec = {
            'repo': 'cool/repo/app1',
            'commands': {
                'once': "one_time.sh",
                'always': "always.sh"
            }
        }
        expected_command_list = ["sh -c \"export PATH=$PATH:/gc/app1",
                                 " if [ ! -f /var/run/dusty/docker_first_time_started ]",
                                 " then touch /var/run/dusty/docker_first_time_started",
                                 " one_time.sh",
                                 " fi",
                                 " always.sh\""]
        returned_command = _compile_docker_command(app_spec).split(";")
        self.assertEqual(expected_command_list, returned_command)

    def test_compile_command_without_once(self, *args):
        app_spec = {
            'repo': 'cool/repo/app1',
            'commands': {
                'always': "always.sh"
            }
        }
        expected_command_list = ["sh -c \"export PATH=$PATH:/gc/app1",
                                 " if [ ! -f /var/run/dusty/docker_first_time_started ]",
                                 " then touch /var/run/dusty/docker_first_time_started",
                                 " fi",
                                 " always.sh\""]
        returned_command = _compile_docker_command(app_spec).split(";")
        self.assertEqual(expected_command_list, returned_command)


    def test_ports_list(self, *args):
        port_spec = {
            'docker_compose': {
                'app1': [
                    { 'mapped_host_port': 8000, 'in_container_port': 1},
                    { 'mapped_host_port': 8005, 'in_container_port': 90}
                ],
                'app2': []
            }
        }
        expected_port_lists = {
            'app1': [
                '8000:1',
                '8005:90'
            ],
            'app2': []
        }
        for app in ['app1', 'app2']:
            self.assertEqual(expected_port_lists[app], _get_ports_list(app, port_spec))

    @patch('dusty.compiler.compose._compile_docker_command', return_value="what command?")
    def test_composed_app(self, *args):
        specs = {
            'apps': {
                'app1': {
                    'repo': '/cool/repo/app1',
                    'depends': {
                        'libs': ['lib1', 'lib2'],
                        'services': ['service1', 'service2'],
                        'apps': ['app2']
                    },
                    'image': 'awesomeGCimage'
                    'mount': '/gc/app1'
                }
            },
            'libs': {
                'lib1': {
                    'repo': '/cool/repo/lib1',
                },
                'lib2': {
                    'repo': '/cool/repo/lib2',
                },
                'lib3': {
                    'repo': '/cool/repo/lib3',
                }
            },
            'services':{
                'service1': {

                },
                'service2': {

                }
            }
        }
        port_spec = {
            'docker_compose': {
                'app1': [
                    { 'mapped_host_port': 8000, 'in_container_port': 1},
                    { 'mapped_host_port': 8005, 'in_container_port': 90}
                ],
                'app2': []
            }
        }
        expected_app_config = {
            'image': 'awesomeGCimage',
            'command': 'what command?',
            'links': [
                'service1',
                'service2',
                'app2'
            ],
            'volumes': [
                '/Users/gc/app1:/gc/app1',
                '/Users/gc/lib1:/gc/lib1',
                '/Users/gc/lib2:/gc/lib2'
            ],
            'ports': [
                '8000:1',
                '8005:90'
            ]
        }
        retured_config = _composed_app_dict('app1', specs, port_spec)
        self.assertEqual(expected_app_config, retured_config)
