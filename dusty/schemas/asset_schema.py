from schemer import Schema, Array

asset_schema = Schema({
    'name': {'type': basestring, 'required': True},
    'path': {'type': basestring, 'required': True},
    'required': {'type': bool, 'default': True}
    })
