from mock import patch, Mock, call

from ...testcases import DustyTestCase
from dusty.commands.status import _has_active_container, get_dusty_status
from dusty.schemas.base_schema_class import DustySchema
from ..utils import get_app_dusty_schema, get_bundle_dusty_schema, get_lib_dusty_schema

class TestStatusCommands(DustyTestCase):
    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_lib_active(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = ['some_container']
        self.assertEquals(False, _has_active_container('lib', 'lib-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_lib_inactive(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = []
        self.assertEquals(False, _has_active_container('lib', 'lib-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_app_active(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = ['some_container']
        self.assertEquals(True, _has_active_container('app', 'app-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_app_inactive(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = []
        self.assertEquals(False, _has_active_container('app', 'app-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_service_active(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = ['some_container']
        self.assertEquals(True, _has_active_container('service', 'service-a'))

    @patch('dusty.commands.status.get_dusty_containers')
    def test_has_active_container_service_inactive(self, fake_get_dusty_containers):
        fake_get_dusty_containers.return_value = []
        self.assertEquals(False, _has_active_container('service', 'service-a'))

    @patch('dusty.commands.status.PrettyTable')
    @patch('dusty.commands.status.get_dusty_containers')
    @patch('dusty.schemas.base_schema_class.get_specs_from_path')
    @patch('dusty.compiler.spec_assembler._get_referenced_apps')
    @patch('dusty.compiler.spec_assembler._get_referenced_libs')
    @patch('dusty.compiler.spec_assembler._get_referenced_services')
    def test_get_dusty_status_active(self, fake_get_services, fake_get_libs, fake_get_apps, fake_get_specs, fake_get_dusty_containers, fake_pretty_table):
        fake_get_services.return_value = set(['ser1', 'ser2', 'ser3'])
        fake_get_libs.return_value = set(['lib1'])
        fake_get_apps.return_value = set(['app1', 'app2'])
        fake_table = Mock()
        fake_pretty_table.return_value = fake_table
        fake_get_dusty_containers.return_value = ['some_container']
        fake_get_specs.return_value = {'apps': {'app1': get_app_dusty_schema({}, 'app1'), 'app2':get_app_dusty_schema({}, 'app2')},
                                       'libs': {'lib1': get_lib_dusty_schema({}, 'lib1')},
                                       'services': {'ser1': DustySchema(None, {}, 'ser1', 'services'), 'ser2': DustySchema(None, {}, 'ser2', 'services'), 'ser3': DustySchema(None, {}, 'ser3', 'services')},
                                       'bundles': get_lib_dusty_schema({})}
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
    @patch('dusty.schemas.base_schema_class.get_specs_from_path')
    @patch('dusty.compiler.spec_assembler._get_referenced_apps')
    @patch('dusty.compiler.spec_assembler._get_referenced_libs')
    @patch('dusty.compiler.spec_assembler._get_referenced_services')
    def test_get_dusty_status_active(self, fake_get_services, fake_get_libs, fake_get_apps, fake_get_specs, fake_get_dusty_containers, fake_pretty_table):
        fake_get_services.return_value = set(['ser1', 'ser2', 'ser3'])
        fake_get_libs.return_value = set(['lib1'])
        fake_get_apps.return_value = set(['app1', 'app2'])
        fake_table = Mock()
        fake_pretty_table.return_value = fake_table
        fake_get_dusty_containers.return_value = []
        fake_get_specs.return_value = {'apps': {'app1': get_app_dusty_schema({}, 'app1'), 'app2':get_app_dusty_schema({}, 'app2')},
                                       'libs': {'lib1': get_lib_dusty_schema({}, 'lib1')},
                                       'services': {'ser1': DustySchema(None, {}, 'ser1', 'services'), 'ser2': DustySchema(None, {}, 'ser2', 'services'), 'ser3': DustySchema(None, {}, 'ser3', 'services')},
                                       'bundles': get_lib_dusty_schema({})}
        get_dusty_status()
        call_args_list = fake_table.add_row.call_args_list
        self.assertTrue(call(['app1', 'app', '']) in call_args_list)
        self.assertTrue(call(['app2', 'app', '']) in call_args_list)
        self.assertTrue(call(['lib1', 'lib', '']) in call_args_list)
        self.assertTrue(call(['ser1', 'service', '']) in call_args_list)
        self.assertTrue(call(['ser2', 'service', '']) in call_args_list)
        self.assertTrue(call(['ser3', 'service', '']) in call_args_list)
        self.assertEquals(len(call_args_list), 6)
