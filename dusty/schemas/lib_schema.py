from schemer import Schema, Array

depends_schema = Schema({
    'libs': {'type': Array(basestring), 'default': list}
    })

test_schema = Schema({}, strict=False)

lib_schema = Schema({
    'repo': {'type': basestring, 'required': True},
    'mount': {'type': basestring, 'default': ''},
    'install': {'type': basestring, 'default': ''},
    'depends': {'type': depends_schema, 'default': dict},
    'test': {'type': test_schema, 'default': dict}
    })
