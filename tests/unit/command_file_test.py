from mock import patch, Mock, call

from ..testcases import DustyTestCase
from .utils import get_lib_dusty_schema, get_app_dusty_schema
from dusty.command_file import (_lib_install_commands, _lib_install_commands_for_app, dusty_command_file_name,
                                make_up_command_files, remove_up_command_files, make_test_command_files,
                                remove_test_command_files)
from dusty.compiler.spec_assembler import get_expanded_libs_specs
from dusty import constants

class TestCommandFile(DustyTestCase):
    def test_lib_install_commands(self, *args):
        lib_spec = {
            'repo': 'some repo',
            'mount': '/mount/point',
            'install': ['python install.py some args']
        }
        expected_command = ["cd /mount/point",  "python install.py some args"]
        actual_command = _lib_install_commands(lib_spec)
        self.assertEqual(expected_command, actual_command)

    def test_lib_install_command_with_no_install_spec(self, *args):
        lib_spec = get_lib_dusty_schema({
            'repo': 'some repo',
            'mount': '/mount/point'
        })
        expected_command = []
        actual_command = _lib_install_commands(lib_spec)
        self.assertEqual(expected_command, actual_command)

    @patch('dusty.command_file._lib_install_commands')
    def test_lib_installs_for_app(self, fake_lib_install, *args):
        basic_specs = {'apps': {'app1': {'depends': {'libs': ['lib1', 'lib2']}}},
                       'libs': {'lib1': {}, 'lib2': {}}}
        _lib_install_commands_for_app('app1', basic_specs)
        # Mock is weird, it picks up on the truthiness calls we do
        # on the result after we call the function
        fake_lib_install.assert_has_calls([call(basic_specs['libs']['lib1']),
                                           call().__nonzero__(),
                                           call().__radd__([]),
                                           call(basic_specs['libs']['lib2']),
                                           call().__nonzero__(),
                                           call().__radd__().__iadd__(fake_lib_install())])

    def test_dusty_command_file_name_basic(self):
        self.assertEquals('dusty_command_file_app.sh', dusty_command_file_name('app'))

    def test_dusty_command_file_name_test(self):
        self.assertEquals('dusty_command_file_app_test_1.sh', dusty_command_file_name('app', test_name='1'))

    def test_dusty_command_file_name_script(self):
        self.assertEquals('dusty_command_file_app_script_1.sh', dusty_command_file_name('app', script_name='1'))

    def test_dusty_command_file_name_both(self):
        self.assertEquals('dusty_command_file_app_script_1.sh', dusty_command_file_name('app', test_name='1', script_name='1'))

    @patch('dusty.command_file._write_commands_to_file')
    def test_make_up_command_files(self, fake_write_commands_to_file):
        assembled_spec = {
            'apps': {'app1': get_app_dusty_schema({'repo': '/gc/app1',
                              'mount': '/gc/app1',
                              'commands': {
                                'once': ['app1 once 1', 'app1 once 2 &'],
                                'always': ['app1 always 1', 'app1 always 2']
                              },
                              'depends': {'libs': ['lib1', 'lib2']},
                              'scripts': [
                                {'name': 'script1', 'description': '', 'command': ['script1 1', 'script1 2']},
                                {'name': 'script2', 'description': '', 'command': ['script2 1', 'script2 2']}]})},
            'libs': {'lib1': get_lib_dusty_schema({'install': ['lib1 command 1', 'lib1 command 2'],
                              'repo': '/gc/lib1',
                              'mount': '/gc/lib1'}),
                     'lib2': get_lib_dusty_schema({'install': ['lib2 command 1', 'lib2 command 2'],
                              'repo': '/gc/lib2',
                              'mount': '/gc/lib2'})}
        }
        make_up_command_files(assembled_spec)

        commands1 = ['cd /gc/lib1',
                     'lib1 command 1',
                     'lib1 command 2',
                     'cd /gc/lib2',
                     'lib2 command 1',
                     'lib2 command 2',
                     'cd /gc/app1',
                     'export PATH=$PATH:/gc/app1',
                     'if [ ! -f {} ]'.format(constants.FIRST_RUN_FILE_PATH),
                     'then mkdir -p {}; touch {}'.format(constants.RUN_DIR, constants.FIRST_RUN_FILE_PATH),
                     'app1 once 1',
                     'app1 once 2 &',
                     'fi',
                     'app1 always 1',
                     'app1 always 2']
        call1 = call(commands1, '{}/gc/app1/dusty_command_file_app1.sh'.format(constants.REPOS_DIR))
        commands2 = ['cd /gc/app1',
                     'script1 1',
                     'script1 2 $@']
        call2 = call(commands2, '{}/gc/app1/dusty_command_file_app1_script_script1.sh'.format(constants.REPOS_DIR))
        commands3 = ['cd /gc/app1',
                     'script2 1',
                     'script2 2 $@']
        call3 = call(commands3, '{}/gc/app1/dusty_command_file_app1_script_script2.sh'.format(constants.REPOS_DIR))

        fake_write_commands_to_file.assert_has_calls([call1, call2, call3])

    @patch('dusty.command_file.os.remove')
    def test_remove_up_command_files(self, fake_remove):
        assembled_spec = {
            'apps': {'app1': get_app_dusty_schema({'repo': '/gc/app1',
                              'mount': '/gc/app1',
                              'commands': {
                                'once': ['app1 once 1', 'app1 once 2 &'],
                                'always': ['app1 always 1', 'app1 always 2']
                              },
                              'depends': {'libs': ['lib1', 'lib2']},
                              'scripts': [
                                {'name': 'script1', 'description': '', 'command': ['script1 1', 'script1 2']},
                                {'name': 'script2', 'description': '', 'command': ['script1 2', 'script2 2']}]})},
            'libs': {'lib1': get_lib_dusty_schema({'install': ['lib1 command 1', 'lib1 command 2'],
                              'repo': '/gc/lib1',
                              'mount': '/gc/lib1'}),
                     'lib2': get_lib_dusty_schema({'install': ['lib2 command 1', 'lib2 command 2'],
                              'repo': '/gc/lib2',
                              'mount': '/gc/lib2'})}
        }
        remove_up_command_files(assembled_spec)
        call1 = call('{}/gc/app1/dusty_command_file_app1.sh'.format(constants.REPOS_DIR))
        call2 = call('{}/gc/app1/dusty_command_file_app1_script_script1.sh'.format(constants.REPOS_DIR))
        call3 = call('{}/gc/app1/dusty_command_file_app1_script_script2.sh'.format(constants.REPOS_DIR))

        fake_remove.assert_has_calls([call1, call2, call3])


    @patch('dusty.command_file._write_commands_to_file')
    @patch('dusty.schemas.base_schema_class.get_specs_from_path')
    def test_make_test_command_files(self, fake_get_specs, fake_write_commands_to_file):
        fake_get_specs.return_value = {
            'apps': {'app1': get_app_dusty_schema({'repo': '/gc/app1',
                              'mount': '/gc/app1',
                              'test': {'once': ['app1 test command 1', 'app1 test command 2'],
                                       'suites': [{'name': 'suite1', 'command': ['suite1 command1', 'suite1 command2']},
                                                  {'name': 'suite2', 'command': ['suite2 command1', 'suite2 command2']}]
                                       }}, name='app1')},
            'libs': {'lib1': get_lib_dusty_schema({'repo': '/gc/lib1',
                              'mount': '/gc/lib1',
                              'test': {'once': ['lib1 test command 1', 'lib1 test command 2'],
                                       'suites': [{'name': 'suite3', 'command': ['suite3 command1', 'suite3 command2']},
                                                  {'name': 'suite4', 'command': ['suite4 command1', 'suite4 command2']}]
                                       }}, name='lib1'),
                     'lib2': get_lib_dusty_schema({}, name='lib2')}
        }
        assembled_spec = get_expanded_libs_specs()
        make_test_command_files(assembled_spec)

        commands1 = ['cd /gc/app1',
                     'app1 test command 1',
                     'app1 test command 2']
        call1 = call(commands1, '{}/gc/app1/dusty_command_file_app1.sh'.format(constants.REPOS_DIR))
        commands2 = ['cd /gc/app1',
                     'suite1 command1',
                     'suite1 command2 $@']
        call2 = call(commands2, '{}/gc/app1/dusty_command_file_app1_test_suite1.sh'.format(constants.REPOS_DIR))
        commands3 = ['cd /gc/app1',
                     'suite2 command1',
                     'suite2 command2 $@']
        call3 = call(commands3, '{}/gc/app1/dusty_command_file_app1_test_suite2.sh'.format(constants.REPOS_DIR))


        commands4 = ['cd /gc/lib1',
                     'lib1 test command 1',
                     'lib1 test command 2']
        call4 = call(commands4, '{}/gc/lib1/dusty_command_file_lib1.sh'.format(constants.REPOS_DIR))
        commands5 = ['cd /gc/lib1',
                     'suite3 command1',
                     'suite3 command2 $@']
        call5 = call(commands5, '{}/gc/lib1/dusty_command_file_lib1_test_suite3.sh'.format(constants.REPOS_DIR))
        commands6 = ['cd /gc/lib1',
                     'suite4 command1',
                     'suite4 command2 $@']
        call6 = call(commands6, '{}/gc/lib1/dusty_command_file_lib1_test_suite4.sh'.format(constants.REPOS_DIR))

        fake_write_commands_to_file.assert_has_calls([call1, call2, call3, call4, call5, call6])

    @patch('dusty.command_file.os.remove')
    @patch('dusty.schemas.base_schema_class.get_specs_from_path')
    def test_remove_test_command_files(self, fake_get_specs, fake_remove):
        fake_get_specs.return_value = {
            'apps': {'app1': get_app_dusty_schema({'repo': '/gc/app1',
                              'mount': '/gc/app1',
                              'test': {'once': ['app1 test command 1', 'app1 test command 2'],
                                       'suites': [{'name': 'suite1', 'command': ['suite1 command1', 'suite1 command2']},
                                                  {'name': 'suite2', 'command': ['suite2 command1', 'suite2 command2']}]
                                       }}, name='app1')},
            'libs': {'lib1': get_lib_dusty_schema({'repo': '/gc/lib1',
                              'mount': '/gc/lib1',
                              'test': {'once': ['lib1 test command 1', 'lib1 test command 2'],
                                       'suites': [{'name': 'suite3', 'command': ['suite3 command1', 'suite3 command2']},
                                                  {'name': 'suite4', 'command': ['suite4 command1', 'suite4 command2']}]
                                       }}, name='lib1'),
                     'lib2': get_lib_dusty_schema({}, name='lib2')}
        }
        assembled_spec = get_expanded_libs_specs()
        remove_test_command_files(assembled_spec)

        call1 = call('{}/gc/app1/dusty_command_file_app1.sh'.format(constants.REPOS_DIR))
        call2 = call('{}/gc/app1/dusty_command_file_app1_test_suite1.sh'.format(constants.REPOS_DIR))
        call3 = call('{}/gc/app1/dusty_command_file_app1_test_suite2.sh'.format(constants.REPOS_DIR))
        call4 = call('{}/gc/lib1/dusty_command_file_lib1.sh'.format(constants.REPOS_DIR))
        call5 = call('{}/gc/lib1/dusty_command_file_lib1_test_suite3.sh'.format(constants.REPOS_DIR))
        call6 = call('{}/gc/lib1/dusty_command_file_lib1_test_suite4.sh'.format(constants.REPOS_DIR))

        fake_remove.assert_has_calls([call1, call2, call3, call4, call5, call6])

