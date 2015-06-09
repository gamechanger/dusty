from schemer import Schema, Array

bundle_schema = Schema({
    'description': {'type': basestring, 'default': ''},
    'apps': {'type': Array(basestring), 'required': True}
    })
