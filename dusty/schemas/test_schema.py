from schemer import Schema, Array

test_suite_schema = Schema({
    'name': {'type': basestring, 'required': True},
    'command': {'type': Array(basestring), 'required': True},
    'default_args': {'type': basestring, 'default': ''},
    'description': {'type': basestring, 'default': ''}
    'compose': {'type': dict, 'default': dict},
    'services': {'type': Array(basestring), 'default': list},
})

test_schema = Schema({
    'image': {'type': basestring},
    'build': {'type': basestring},
    'once': {'type': Array(basestring), 'default': []},
    'suites': {'type': Array(test_suite_schema), 'default': list},
    })
