from mock import patch, call

from dusty.commands.run import restart_apps_or_services, restart_apps_by_repo
from dusty.source import Repo
from ...testcases import DustyTestCase
from ..utils import apply_required_keys

class TestRunCommands(DustyTestCase):
    def setUp(self):
        super(TestRunCommands, self).setUp()
        self.specs = self.make_test_specs(apply_required_keys({
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
                        'apps': [],
                        'libs': []
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
        }))

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.nfs')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.commands.run.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_with_arguments_1(self, fake_get_assembled_specs, fake_get_specs, fake_nfs, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(['app-a', 'app-b'])
        fake_nfs.update_nfs_with_repos.assert_has_calls([call(set([Repo('github.com/app/a'), Repo('github.com/app/b'),
            Repo('github.com/lib/a'), Repo('github.com/lib/b')]))])

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.nfs')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.commands.run.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_with_arguments_2(self, fake_get_assembled_specs, fake_get_specs, fake_nfs, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(['app-a', 'app-b', 'ser-a'])
        fake_nfs.update_nfs_with_repos.assert_has_calls([call(set([Repo('github.com/app/a'), Repo('github.com/app/b'),
            Repo('github.com/lib/a'), Repo('github.com/lib/b')]))])

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.nfs')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.commands.run.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_with_arguments_3(self, fake_get_assembled_specs, fake_get_specs, fake_nfs, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(['app-a', 'ser-a'])
        fake_nfs.update_nfs_with_repos.assert_has_calls([call(set([Repo('github.com/app/a'),
            Repo('github.com/lib/a'), Repo('github.com/lib/b')]))])

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.nfs')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_without_arguments_1(self, fake_get_assembled_specs, fake_get_specs, fake_nfs, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services()
        fake_nfs.update_nfs_with_repos.assert_has_calls([call(set([Repo('github.com/app/a'), Repo('github.com/app/b'),
                                                          Repo('github.com/lib/a'), Repo('github.com/lib/b')]))])

    @patch('dusty.commands.run.docker.compose.restart_running_services')
    @patch('dusty.commands.run.nfs')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_or_services_without_arguments_no_sync(self, fake_get_assembled_specs, fake_get_specs, fake_nfs, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_or_services(sync=False)

    @patch('dusty.commands.run.restart_apps_or_services')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_by_repo_lib(self, fake_get_assembled_specs, fake_get_specs, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_by_repo(['github.com/lib/b'])
        fake_restart.assert_has_calls([call(set(['app-a']), sync=True)])

    @patch('dusty.commands.run.restart_apps_or_services')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_by_repo_app(self, fake_get_assembled_specs, fake_get_specs, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_by_repo(['github.com/app/b'])
        fake_restart.assert_has_calls([call(set(['app-b']), sync=True)])

    @patch('dusty.commands.run.restart_apps_or_services')
    @patch('dusty.commands.run.spec_assembler.get_specs')
    @patch('dusty.compiler.spec_assembler.get_assembled_specs')
    def test_restart_apps_by_repo_both(self, fake_get_assembled_specs, fake_get_specs, fake_restart):
        fake_get_assembled_specs.return_value = self.specs
        fake_get_specs.return_value = self.specs
        restart_apps_by_repo(['github.com/lib/b', 'github.com/app/b'])
        fake_restart.assert_has_calls([call(set(['app-a', 'app-b']), sync=True)])

