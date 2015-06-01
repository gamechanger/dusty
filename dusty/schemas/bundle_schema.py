from schemer import Schema, Array

bundle_schema = Schema({
    'description': {'type': basestring},
    'apps': {'type': Array(basestring), 'required': True}
    })
