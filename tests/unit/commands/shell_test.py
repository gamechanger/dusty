from mock import patch

from ...testcases import DustyTestCase
from dusty.commands.shell import execute_shell

class TestShellCommands(DustyTestCase):
    def test_execute_script_nonexistent_app(self):
        with self.assertRaises(KeyError):
            execute_shell('some-nonexistent-app')

    @patch('dusty.commands.shell.exec_docker')
    def test_execute_script_valid_app(self, fake_exec_docker):
        execute_shell('app-a')
        fake_exec_docker.assert_called_once_with('exec', '-ti', 'dusty_app-a_1', '/bin/bash')

    @patch('dusty.commands.shell.exec_docker')
    def test_execute_script_valid_service(self, fake_exec_docker):
        execute_shell('service-a')
        fake_exec_docker.assert_called_once_with('exec', '-ti', 'dusty_service-a_1', '/bin/bash')
