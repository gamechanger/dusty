from mock import patch, call

from ....testcases import DustyTestCase
from dusty.systems.rsync import sync_repos_by_app_name, sync_repos_by_lib_name
from dusty.source import Repo

class TestRysnc(DustyTestCase):

    @patch('dusty.systems.rsync.sync_repos')
    @patch('dusty.compiler.spec_assembler.get_specs')
    def test_sync_repos_by_app_name_1(self, fake_get_specs, fake_sync_repos):
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
        fake_get_specs.return_value = specs
        sync_repos_by_app_name(specs, ['app-a', 'app-b'])
        fake_sync_repos.assert_has_calls([call(set([Repo('github.com/app/a'), Repo('github.com/app/b'), Repo('github.com/lib/a'), Repo('github.com/lib/b')]))])


    @patch('dusty.systems.rsync.sync_repos')
    @patch('dusty.compiler.spec_assembler.get_specs')
    def test_sync_repos_by_app_name_2(self, fake_get_specs, fake_sync_repos):
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
        fake_get_specs.return_value = specs
        sync_repos_by_app_name(specs, ['app-a'])
        fake_sync_repos.assert_has_calls([call(set([Repo('github.com/app/a'), Repo('github.com/lib/a'), Repo('github.com/lib/b')]))])

    @patch('dusty.systems.rsync.sync_repos')
    @patch('dusty.compiler.spec_assembler.get_specs')
    def test_sync_repos_by_lib_name_1(self, fake_get_specs, fake_sync_repos):
        specs = {
            'apps': {
                'app-a': {
                    'repo': 'github.com/app/a',
                    'depends': {
                        'apps': ['app-b'],
                        'libs': ['lib-a', 'lib-b']
                    }
                },
            },
            'libs': {
                'lib-a':{
                    'repo': 'github.com/lib/a',
                    'depends': {'libs': ['lib-b']}
                },
                'lib-b':{
                    'depends': {'libs': ['lib-c']},
                    'repo': 'github.com/lib/b'},
                'lib-c':{
                    'depends': {},
                    'repo': 'github.com/lib/c'}
            }
        }
        fake_get_specs.return_value = specs
        sync_repos_by_lib_name(specs, ['lib-a'])
        fake_sync_repos.assert_has_calls([call(set([Repo('github.com/lib/a'), Repo('github.com/lib/b')]))])


    @patch('dusty.systems.rsync.sync_repos')
    @patch('dusty.compiler.spec_assembler.get_specs')
    def test_sync_repos_by_lib_name_2(self, fake_get_specs, fake_sync_repos):
        specs = {
            'apps': {},
            'libs': {
                'lib-a':{
                    'repo': 'github.com/lib/a',
                    'depends': {'libs': ['lib-c']}
                },
                'lib-b':{
                    'repo': 'github.com/lib/b',
                    'depends': {'libs': ['lib-d']}
                },
                'lib-c': {
                    'repo': 'github.com/lib/c',
                    'depends': {}
                },
                'lib-d': {
                    'repo': 'github.com/lib/d',
                    'depends': {}
                }
            }
        }
        fake_get_specs.return_value = specs
        sync_repos_by_lib_name(specs, ['lib-a', 'lib-b'])
        fake_sync_repos.assert_has_calls([call(set([Repo('github.com/lib/a'), Repo('github.com/lib/b'), Repo('github.com/lib/c'), Repo('github.com/lib/d')]))])
