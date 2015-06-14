from schemer import Schema, Array

test_suite_schema = Schema({
    'name': {'type': basestring, 'required': True},
    'command': {'type': basestring, 'required': True},
    'default_args': {'type': basestring, 'default': ''},
    'description': {'type': basestring, 'default': ''}
})

test_schema = Schema({
    'image': {'type': basestring, 'default': ''},
    'build': {'type': basestring},
    'services': {'type': Array(basestring), 'default': list},
    'once': {'type': basestring},
    'compose': {'type': dict, 'default': dict},
    'suites': {'type': Array(test_suite_schema), 'default': list},
    })
