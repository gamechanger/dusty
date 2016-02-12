from schemer import Schema, Array

def no_all_suite_validator():
    def validator(document):
        for suite in document.get('suites', []):
            if suite['name'].upper() == 'ALL':
                return 'all is a reserved suite name. It cannot be used in a spec.'
    return validator

test_suite_schema = Schema({
    'name': {'type': basestring, 'required': True},
    'command': {'type': Array(basestring), 'required': True},
    'default_args': {'type': basestring, 'default': ''},
    'description': {'type': basestring, 'default': ''},
    'compose': {'type': dict, 'default': dict},
    'services': {'type': Array(basestring), 'default': list},
})

test_schema = Schema({
    'image': {'type': basestring},
    'image_requires_login': {'type': bool, 'default': False},
    'build': {'type': basestring},
    'once': {'type': Array(basestring), 'default': []},
    'suites': {'type': Array(test_suite_schema), 'default': list},
    }, validates=[no_all_suite_validator()])
