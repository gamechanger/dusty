from schemer import Schema, Array

from .test_schema import test_schema
from .asset_schema import asset_schema

depends_schema = Schema({
    'libs': {'type': Array(basestring), 'default': list}
    })

lib_schema = Schema({
    'repo': {'type': basestring, 'required': True},
    'mount': {'type': basestring, 'default': '', 'required': True},
    'install': {'type': Array(basestring), 'default': list},
    'depends': {'type': depends_schema, 'default': dict},
    'assets': {'type': Array(asset_schema), 'default': list},
    'test': {'type': test_schema, 'default': dict}
    })
