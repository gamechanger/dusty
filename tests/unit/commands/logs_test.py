from mock import patch

from ...testcases import DustyTestCase
from dusty.commands.logs import tail_container_logs

class TestLogsCommands(DustyTestCase):
    @patch('dusty.commands.logs.exec_docker')
    @patch('dusty.commands.logs.get_dusty_containers')
    def test_tail_container_logs(self, fake_get_containers, fake_exec_docker):
        fake_get_containers.return_value = [{'Id': 'container-id'}]
        tail_container_logs('app-a')
        fake_get_containers.assert_called_once_with(['app-a'])
        fake_exec_docker.assert_called_once_with('logs', 'container-id')

    @patch('dusty.commands.logs.exec_docker')
    @patch('dusty.commands.logs.get_dusty_containers')
    def test_tail_with_line_number(self, fake_get_containers, fake_exec_docker):
        fake_get_containers.return_value = [{'Id': 'container-id'}]
        tail_container_logs('app-a', lines=4)
        fake_get_containers.assert_called_once_with(['app-a'])
        fake_exec_docker.assert_called_once_with('logs', '--tail=4', 'container-id')

    @patch('dusty.commands.logs.exec_docker')
    @patch('dusty.commands.logs.get_dusty_containers')
    def test_tail_container_logs_with_follow(self, fake_get_containers, fake_exec_docker):
        fake_get_containers.return_value = [{'Id': 'container-id'}]
        tail_container_logs('app-a', follow=True)
        fake_get_containers.assert_called_once_with(['app-a'])
        fake_exec_docker.assert_called_once_with('logs', '-f', 'container-id')

    @patch('dusty.commands.logs.exec_docker')
    @patch('dusty.commands.logs.get_dusty_containers')
    def test_tail_with_line_number(self, fake_get_containers, fake_exec_docker):
        fake_get_containers.return_value = [{'Id': 'container-id'}]
        tail_container_logs('app-a', follow=True, lines=4)
        fake_get_containers.assert_called_once_with(['app-a'])
        fake_exec_docker.assert_called_once_with('logs', '-f', '--tail=4', 'container-id')
