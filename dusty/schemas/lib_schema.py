from schemer import Schema, Array

from .test_schema import test_schema

depends_schema = Schema({
    'libs': {'type': Array(basestring), 'default': list}
    })

lib_schema = Schema({
    'repo': {'type': basestring, 'required': True},
    'mount': {'type': basestring, 'default': ''},
    'install': {'type': basestring, 'default': ''},
    'depends': {'type': depends_schema, 'default': dict},
    'test': {'type': test_schema, 'default': dict}
    })
