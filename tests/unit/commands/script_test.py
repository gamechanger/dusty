from mock import patch

from ..utils import DustyTestCase
from dusty.commands.script import script_info_for_app, execute_script

class TestScriptCommands(DustyTestCase):
    def test_script_info_for_app_nonexistent_app(self):
        with self.assertRaises(KeyError):
            script_info_for_app('some-nonexistent-app')

    def test_script_info_for_app_no_scripts(self):
        script_info_for_app('app-b')
        self.assertEqual(self.last_client_output, 'No scripts registered for app app-b')

    def test_script_info_for_app_valid_input(self):
        script_info_for_app('app-a')
        spec_line = self.last_client_output.splitlines()[3]
        self.assertIn('A script description', spec_line)
        self.assertIn('example', spec_line)

    def test_execute_script_nonexistent_app(self):
        with self.assertRaises(KeyError):
            execute_script('some-nonexistent-app', 'this arg should not matter')

    def test_execute_script_no_scripts(self):
        with self.assertRaises(KeyError):
            execute_script('app-b', 'should not matter')

    def test_execute_script_script_not_found(self):
        with self.assertRaises(KeyError):
            execute_script('app-a', 'wrong name')

    @patch('dusty.commands.script.exec_docker')
    def test_execute_script_valid_input(self, fake_exec_docker):
        execute_script('app-a', 'example')
        fake_exec_docker.assert_called_once_with('exec', '-ti', 'dusty_app-a_1', 'sh', '-c', 'ls /')

    @patch('dusty.commands.script.exec_docker')
    def test_execute_script_valid_input_one_arg(self, fake_exec_docker):
        execute_script('app-a', 'example', ['.'])
        fake_exec_docker.assert_called_once_with('exec', '-ti', 'dusty_app-a_1', 'sh', '-c', 'ls / .')

    @patch('dusty.commands.script.exec_docker')
    def test_execute_script_valid_input_three_args(self, fake_exec_docker):
        execute_script('app-a', 'example', ['.', './', '..'])
        fake_exec_docker.assert_called_once_with('exec', '-ti', 'dusty_app-a_1', 'sh', '-c', 'ls / . ./ ..')
