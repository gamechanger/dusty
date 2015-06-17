from mock import patch, Mock, call

from ...testcases import DustyTestCase
from dusty.commands.status import _has_activate_container, get_dusty_status

class TestStatusCommands(DustyTestCase):
    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_lib_active(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = ['some_container']
        self.assertEquals(False, _has_activate_container('libs', 'lib-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_lib_inactive(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = []
        self.assertEquals(False, _has_activate_container('libs', 'lib-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_app_active(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = ['some_container']
        self.assertEquals(True, _has_activate_container('app', 'app-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_app_inactive(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = []
        self.assertEquals(False, _has_activate_container('app', 'app-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_service_active(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = ['some_container']
        self.assertEquals(True, _has_activate_container('service', 'service-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_service_inactive(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = []
        self.assertEquals(False, _has_activate_container('service', 'service-a'))

    @patch('dusty.commands.status.PrettyTable')
    @patch('dusty.commands.status.get_dusty_containers')
    @patch('dusty.commands.status.get_assembled_specs')
    def test_get_dusty_status_active(self, fake_get_specs, fake_get_dusty_containers, fake_pretty_table):
        fake_table = Mock()
        fake_pretty_table.return_value = fake_table
        fake_get_dusty_containers.return_value = ['some_container']
        fake_get_specs.return_value = {'apps': {'app1': {}, 'app2':{}},
                                       'libs': {'lib1': {}},
                                       'services': {'ser1': {}, 'ser2': {}, 'ser3': {}}}
        get_dusty_status()
        call_args_list = fake_table.add_row.call_args_list
        self.assertTrue(call(['app1', 'app', 'X']) in call_args_list)
        self.assertTrue(call(['app2', 'app', 'X']) in call_args_list)
        self.assertTrue(call(['lib1', 'lib', '']) in call_args_list)
        self.assertTrue(call(['ser1', 'service', 'X']) in call_args_list)
        self.assertTrue(call(['ser2', 'service', 'X']) in call_args_list)
        self.assertTrue(call(['ser3', 'service', 'X']) in call_args_list)
        self.assertEquals(len(call_args_list), 6)

    @patch('dusty.commands.status.PrettyTable')
    @patch('dusty.commands.status.get_dusty_containers')
    @patch('dusty.commands.status.get_assembled_specs')
    def test_get_dusty_status_non_active(self, fake_get_specs, fake_get_dusty_containers, fake_pretty_table):
        fake_table = Mock()
        fake_pretty_table.return_value = fake_table
        fake_get_dusty_containers.return_value = []
        fake_get_specs.return_value = {'apps': {'app1': {}, 'app2':{}},
                                       'libs': {'lib1': {}},
                                       'services': {'ser1': {}, 'ser2': {}, 'ser3': {}}}
        get_dusty_status()
        call_args_list = fake_table.add_row.call_args_list
        self.assertTrue(call(['app1', 'app', '']) in call_args_list)
        self.assertTrue(call(['app2', 'app', '']) in call_args_list)
        self.assertTrue(call(['lib1', 'lib', '']) in call_args_list)
        self.assertTrue(call(['ser1', 'service', '']) in call_args_list)
        self.assertTrue(call(['ser2', 'service', '']) in call_args_list)
        self.assertTrue(call(['ser3', 'service', '']) in call_args_list)
        self.assertEquals(len(call_args_list), 6)
