from mock import patch, call

from ....testcases import DustyTestCase
from dusty.systems.rsync import sync_repos_by_app_name

class TestRysnc(DustyTestCase):

    @patch('dusty.systems.rsync.sync_repos')
    @patch('dusty.systems.rsync.get_assembled_specs')
    @patch('dusty.compiler.spec_assembler.get_specs')
    def test_sync_repos_by_app_name_1(self, fake_get_specs, fake_get_assembled_specs, fake_sync_repos):
        specs = {
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
        fake_get_assembled_specs.return_value = specs
        fake_get_specs.return_value = specs
        sync_repos_by_app_name(['app-a', 'app-b'])
        fake_sync_repos.assert_has_calls([call(set(['github.com/app/a', 'github.com/app/b', 'github.com/lib/a', 'github.com/lib/b']))])


    @patch('dusty.systems.rsync.sync_repos')
    @patch('dusty.systems.rsync.get_assembled_specs')
    @patch('dusty.compiler.spec_assembler.get_specs')
    def test_sync_repos_by_app_name_2(self, fake_get_specs, fake_get_assembled_specs, fake_sync_repos):
        specs = {
            'apps': {
                'app-a': {
                    'repo': 'github.com/app/a',
                    'depends': {
                        'libs': ['lib-a', 'lib-b']
                    }
                }
            },
            'libs': {
                'lib-a':{
                    'repo': 'github.com/lib/a',
                    'depends': {'libs': ['lib-b']}
                },
                'lib-b':{
                    'repo': 'github.com/lib/b'}
            }
        }
        fake_get_assembled_specs.return_value = specs
        fake_get_specs.return_value = specs
        sync_repos_by_app_name(['app-a'])
        fake_sync_repos.assert_has_calls([call(set(['github.com/app/a', 'github.com/lib/a', 'github.com/lib/b']))])
