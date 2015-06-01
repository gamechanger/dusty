from schemer import Schema, Array

depends_schema = Schema({
    'libs': {'type': Array(basestring)}
    })

lib_schema = Schema({
    'repo': {'type': basestring, 'required': True},
    'mount': {'type': basestring},
    'install': {'type': basestring},
    'depends': {'type': depends_schema}
    })
