from mock import patch
import os
import yaml

from dusty.compiler.spec_assembler import get_specs_path
from dusty.schemas.base_schema_class import DustySchema, DustySpecs
from dusty.schemas.app_schema import app_schema

def _num_to_alpha(num):
    if num >= 26:
        raise ValueError('Only supports up to 26')
    return chr(num + 97)

def _write(spec_type, name, spec_doc):
    spec_type_path = os.path.join(get_specs_path(), '{}s'.format(spec_type))
    try:
        os.makedirs(spec_type_path)
    except OSError:
        pass
    with open(os.path.join(spec_type_path, '{}.yml'.format(name)), 'w') as f:
        f.write(yaml.dump(spec_doc, default_flow_style=False))

def premade_app():
    return DustySchema(app_schema, {'repo': '/tmp/fake-repo',
                                    'mount': '/repo',
                                    'image': 'busybox',
                                    'commands': {'always': ['sleep 999999999']}},
                       'fake_app', 'apps')

def single_specs_fixture():
    _write('bundle', 'bundle-a', {'description': 'Bundle A', 'apps': ['appa']})
    _write('app', 'appa', {'repo': 'github.com/app/a',
                            'commands': {
                                'always': ['sleep 9999999']
                            },
                            'image': 'busybox',
                            'mount': '/app/a',
                            'scripts': [
                                {'description': 'A script description',
                                 'command': ['touch /app/a/foo'],
                                 'name': 'example'},
                                {'description': 'A rm script',
                                 'command': ['rm'],
                                 'name': 'example_rm'},
                                {'description': 'An ls script',
                                 'command': ['ls'],
                                 'name': 'example_ls'},
                                {'description': 'A touch script',
                                 'command': ['touch'],
                                 'name': 'example_touch'}]})

def basic_specs_fixture():
    _write('bundle', 'bundle-a', {'description': 'Bundle A', 'apps': ['app-a']})
    _write('bundle', 'bundle-b', {'description': 'Bundle B', 'apps': ['app-b']})
    _write('app', 'app-a', {'repo': 'github.com/app/a',
                            'image': 'app/a',
                            'mount': '/app/a',
                            'scripts': [{'description': 'A script description',
                                        'command': ['ls /'],
                                        'name': 'example'}]})
    _write('app', 'app-b', {'repo': 'github.com/app/b',
                            'image': 'app/b',
                            'mount': '/app/b',
                            'scripts': [{'description': 'A script description',
                                        'command': ['ls /'],
                                        'name': 'example'}]})
    _write('app', 'app-c', {'repo': '/gc/repos/c',
                            'image': 'app/c',
                            'mount': '/app/c',})
    _write('lib', 'lib-a', {'repo': 'github.com/lib/a',
                            'mount': '/lib/a',})
    _write('service', 'service-a', {'image': 'service/a'})

def specs_fixture_with_depends():
    _write('bundle', 'bundle-a', {'description': 'Bundle A', 'apps': ['appa']})
    _write('bundle', 'bundle-b', {'description': 'Bundle B', 'apps': ['appb', 'appc']})
    _write('app', 'appa', {'repo': '/tmp/repo-app-a',
                           'commands': {
                               'always': ['sleep 1000']
                           },
                            'image': 'busybox',
                           'mount': '/app/a',
                           'scripts': [{'description': 'A script description',
                                        'command': ['ls /'],
                                        'name': 'example'}],
                           'depends': {
                               'libs': ['lib-a']
                           }})
    _write('app', 'appb', {'repo': '/tmp/repo-app-b',
                           'commands': {
                               'always': ['sleep 1000']
                           },
                            'image': 'busybox',
                           'mount': '/app/b',
                           'scripts': [{'description': 'A script description',
                                        'command': ['ls /'],
                                        'name': 'example'}],
                           'depends': {
                               'apps': ['appa'],
                               'libs': ['lib-b']
                           }})
    _write('app', 'appc', {'repo': '/tmp/repo-app-c',
                           'mount': '/app/c',
                           'commands': {
                               'always': ['sleep 1000']
                           },
                           'image': 'busybox',})
    _write('lib', 'lib-a', {'repo': '/tmp/repo-lib-a',
                            'mount': '/lib/a',})
    _write('lib', 'lib-b', {'repo': '/tmp/repo-lib-b',
                            'mount': '/lib/b',
                            'depends': {
                                'libs': ['lib-a']
                            }})
    _write('service', 'servica', {'image': 'busybox'})

def fixture_with_commands(once_fail=False, always_fail=False):
    once_commands = ['touch /once_test_file', 'echo "once ran" | tee -a /once_test_file']
    always_commands = ['touch /always_test_file', 'echo "always ran" | tee -a /always_test_file', 'sleep 999999']
    if once_fail:
        once_commands = ['stdbuf -i0 -o0 -e0 echo "once starting"', 'random-command', 'echo "once ran"']
    if always_fail:
        always_commands = ['echo "always starting"', 'random-command', 'echo "always ran"']
    _write('bundle', 'bundle-a', {'description': 'Bundle A', 'apps': ['appa']})
    _write('app', 'appa', {'commands': {
                                'once': once_commands,
                                'always': always_commands
                            },
                            'image': 'python',
                          })

def busybox_single_app_bundle_fixture(num_bundles=1, command=['sleep 999999999']):
    """Fixture for use in integration tests. The local repo at
    /tmp/fake-repo should be set up before using this fixture."""
    app_dict = {'repo': '/tmp/fake-repo',
                'mount': '/repo',
                'image': 'busybox',
                'commands': {'always': command},
                'test': {'image': 'python',
                            'once': ['pip install nose'],
                            'suites': [{'name': 'test1',
                                        'command': ['nosetests'],
                                        'default_args': '.'},
                                        {'name': 'test2',
                                        'command': ['nosetests'],
                                        'default_args': '.'},
                                        {'name': 'test3',
                                        'command': ['ls'],
                                        'default_args': '.'}]}}
    for bundle in range(num_bundles):
        name = 'busybox{}'.format(_num_to_alpha(bundle))
        _write('bundle', name, {'description': 'Busybox bundle', 'apps': [name]})
        _write('app', name, app_dict)

def invalid_fixture():
    _write('app', 'invalid', {'spaghetti': 'meatballs'})
