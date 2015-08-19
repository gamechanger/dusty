from schemer import Schema, Array

def app_or_service_required_validator():
    def validator(document):
        if 'apps' not in document and 'services' not in document:
            return 'Bundles must specify `apps` or `services`'
    return validator

bundle_schema = Schema({
    'description': {'type': basestring, 'default': ''},
    'apps': {'type': Array(basestring), 'default': list},
    'services': {'type': Array(basestring), 'default': list},
    }, validates=[app_or_service_required_validator()])
