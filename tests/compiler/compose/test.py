from unittest import TestCase
from mock import patch, call
from copy import copy

from dusty import constants
from dusty.compiler.compose import (get_compose_dict, _composed_app_dict, _composed_service_dict,
                                    _get_ports_list, _compile_docker_command, _get_compose_volumes,
                                    _lib_install_command, _lib_install_commands_for_app)
from ..test_test_cases import all_test_configs

basic_specs = {
    'apps': {
        'app1': {
            'repo': '/cool/repo/app1',
            'depends': {
                'libs': ['lib1', 'lib2'],
                'services': ['service1', 'service2'],
                'apps': ['app2']
            },
            'commands': {
                'once': "one_time.sh",
                'always': "always.sh"
            },
            'image': 'awesomeGCimage',
            'mount': '/gc/app1'
        }
    },
    'libs': {
        'lib1': {
            'repo': '/cool/repo/lib1',
            'mount': '/gc/lib1',
            'install': './install.sh'
        },
        'lib2': {
            'repo': '/cool/repo/lib2',
            'mount': '/gc/lib2',
            'install': 'python setup.py develop'
        },
        'lib3': {
            'repo': '/cool/repo/lib3',
            'mount': '/gc/lib3',
            'intstall': 'blah'
        }
    },
    'services':{
        'service1': {

        },
        'service2': {

        }
    }
}

basic_port_specs = {
    'docker_compose': {
        'app1': [
            { 'mapped_host_port': 8000, 'in_container_port': 1},
            { 'mapped_host_port': 8005, 'in_container_port': 90}
        ],
        'app2': []
    }
}


def vm_repo_path(name):
    return "/Users/gc/{}".format(name.split('/')[-1])

@patch('dusty.compiler.compose.vm_repo_path', side_effect=vm_repo_path)
class TestComposeCompiler(TestCase):
    def test_composed_volumes(self, *args):
        expected_volumes = [
            '/Users/gc/app1:/gc/app1',
            '/Users/gc/lib1:/gc/lib1',
            '/Users/gc/lib2:/gc/lib2'
        ]
        returned_volumes = _get_compose_volumes('app1', basic_specs)
        self.assertEqual(expected_volumes, returned_volumes)

    def test_compile_command_with_once(self, *args):
        expected_command_list = ["sh -c \"cd /gc/lib1 && ./install.sh",
                                 " cd /gc/lib2 && python setup.py develop",
                                 " cd /gc/app1",
                                 " export PATH=$PATH:/gc/app1",
                                 " if [ ! -f /var/run/dusty/docker_first_time_started ]",
                                 " then mkdir -p /var/run/dusty",
                                 " touch /var/run/dusty/docker_first_time_started",
                                 " one_time.sh",
                                 " fi",
                                 " always.sh\""]
        returned_command = _compile_docker_command('app1', basic_specs).split(";")
        self.assertEqual(expected_command_list, returned_command)

    def test_compile_command_without_once(self, *args):
        new_specs = copy(basic_specs)
        del new_specs['apps']['app1']['commands']['once']
        expected_command_list = ["sh -c \"cd /gc/lib1 && ./install.sh",
                                 " cd /gc/lib2 && python setup.py develop",
                                 " cd /gc/app1",
                                 " export PATH=$PATH:/gc/app1",
                                 " if [ ! -f /var/run/dusty/docker_first_time_started ]",
                                 " then mkdir -p /var/run/dusty",
                                 " touch /var/run/dusty/docker_first_time_started",
                                 " fi",
                                 " always.sh\""]
        returned_command = _compile_docker_command('app1', new_specs).split(";")
        self.assertEqual(expected_command_list, returned_command)

    def test_ports_list(self, *args):
        expected_port_lists = {
            'app1': [
                '8000:1',
                '8005:90'
            ],
            'app2': []
        }
        for app in ['app1', 'app2']:
            self.assertEqual(expected_port_lists[app], _get_ports_list(app, basic_port_specs))

    @patch('dusty.compiler.compose._compile_docker_command', return_value="what command?")
    def test_composed_app(self, *args):
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
        retured_config = _composed_app_dict('app1', basic_specs, basic_port_specs)
        self.assertEqual(expected_app_config, retured_config)

    def test_lib_install_command(self, *args):
        lib_spec = {
            'repo': 'some repo',
            'mount': '/mount/point',
            'install': 'python install.py some args'
        }
        expected_command = "cd /mount/point && python install.py some args"
        actual_command = _lib_install_command(lib_spec)
        self.assertEqual(expected_command, actual_command)

    @patch('dusty.compiler.compose._lib_install_command')
    def test_lib_installs_for_app(self, fake_lib_install, *args):
        _lib_install_commands_for_app('app1', basic_specs)
        fake_lib_install.assert_has_calls([call(basic_specs['libs']['lib1']), call(basic_specs['libs']['lib2'])])
