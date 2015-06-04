from mock import patch, call

from dusty.commands.run import restart_apps_or_services
from ...testcases import DustyTestCase

class TestRunCommands(DustyTestCase):
    def setUp(self):
        super(TestRunCommands, self).setUp()
        self.specs = {
            'apps': {
                'app-a': {
                    'repo': 'github.com/app/a',
                    'depends': {
                        'apps': ['app-b'],
                        'libs': ['lib-a', 'lib-b']
                    }
                },
                'app-b': {
                    'depends': {
                        'apps': {},
                        'libs': {}
                    },
                    'repo': 'github.com/app/b'}
            },
            'libs': {
                'lib-a':{
                    'repo': 'github.com/lib/a',
                    'depends': {'libs': ['lib-b']}
                },
                'lib-b':{
                    'depends': {},
                    'repo': 'github.com/lib/b'}
            }
        }

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.rsync')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_with_arguments_1(self,fake_get_assembled_specs, fake_get_specs, fake_rsync, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(['app-a', 'app-b'])
        fake_rsync.sync_repos_by_app_name.assert_has_calls([call(['app-a', 'app-b'])])

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.rsync')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_with_arguments_no_sync(self,fake_get_assembled_specs, fake_get_specs, fake_rsync, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(['app-a', 'app-b'], sync=False)
        self.assertFalse(fake_rsync.sync_repos_by_app_name.called)

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.rsync')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_with_arguments_2(self,fake_get_assembled_specs, fake_get_specs, fake_rsync, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(['app-a', 'app-b', 'ser-a'])
        fake_rsync.sync_repos_by_app_name.assert_has_calls([call(['app-a', 'app-b'])])

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.rsync')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_with_arguments_3(self,fake_get_assembled_specs, fake_get_specs, fake_rsync, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(['app-a', 'ser-a'])
        fake_rsync.sync_repos_by_app_name.assert_has_calls([call(['app-a'])])

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.rsync')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_without_arguments_1(self,fake_get_assembled_specs, fake_get_specs, fake_rsync, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services()
        fake_rsync.sync_repos.assert_has_calls([call(set(['github.com/app/a', 'github.com/app/b', 'github.com/lib/a', 'github.com/lib/b']))])

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.rsync')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_without_arguments_no_sync(self,fake_get_assembled_specs, fake_get_specs, fake_rsync, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(sync=False)
        self.assertFalse(fake_rsync.sync_repos.called)
