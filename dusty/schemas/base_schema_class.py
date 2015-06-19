import collections
from copy import deepcopy
import glob
import os
import yaml

from schemer import ValidationException

from . import app_schema, lib_schema, bundle_schema
from ..log import log_to_client

class BaseMutable(collections.MutableMapping):
    def __init__(self, document):
        self._document = document

    def __getitem__(self, name):
        return self._document[name]

    def __setitem__(self, key, value):
        self._document[key] = value

    def __delitem__(self, key):
        del self._document[key]

    def __contains__(self, key):
        return key in self._document

    def __iter__(self):
        return iter(self._document)

    def __len__(self):
        return len(self._document)

    def keys(self):
        return self._document.keys()

    def values(self):
        return self._document.values()

    def plain_dict(self):
        return self._document


def _get_respective_schema(specs_type):
    if specs_type == 'apps':
        return app_schema
    elif specs_type == 'bundles':
        return bundle_schema
    elif specs_type == 'libs':
        return lib_schema
    elif specs_type == 'services':
        return None
    else:
        raise RuntimeError('Specs must be of the type apps, bundles, libs or services')

def notifies_validation_exception(f):
    def inner(spec, *args):
        try:
            f(spec, *args)
        except ValidationException as e:
            log_to_client("Error validating {} {}: {}".format(spec.type_singular, spec.name, str(e)))
            raise e
    return inner

# This is build on top of Schemer's functionality
class DustySchema(BaseMutable):
    def __init__(self, schema, document, name=None, spec_type=None):
        self.name = name
        self.spec_type = spec_type
        if isinstance(spec_type, basestring):
            self.type_singular = spec_type.rstrip('s')
        self.validate(schema, document)
        self._document = deepcopy(document)
        super(DustySchema, self).__init__(deepcopy(document))
        if schema is not None:
            schema.apply_defaults(self._document)

    @notifies_validation_exception
    def validate(self, schema, document):
        if schema is not None:
            schema.validate(document)

def get_specs_from_path(specs_path):
    specs = {}
    for key in ['bundles', 'apps', 'libs', 'services']:
        specs[key] = {}
        schema = _get_respective_schema(key)
        key_path = os.path.join(specs_path, key)
        for spec_path in glob.glob('{}/*.yml'.format(key_path)):
            spec_name = os.path.splitext(os.path.split(spec_path)[-1])[0]
            with open(spec_path, 'r') as f:
                spec = yaml.load(f.read())
                spec = DustySchema(schema, spec, spec_name, key)
                specs[key][spec_name] = spec
    return specs

class DustySpecs(BaseMutable):
    def __init__(self, specs_path):
        document = get_specs_from_path(specs_path)
        super(DustySpecs, self).__init__(document)

    def get_app_or_lib(self, app_or_lib_name):
        if app_or_lib_name in self._document['apps']:
            return self._document['apps'][app_or_lib_name]
        elif app_or_lib_name in self._document['libs']:
            return self._document['libs'][app_or_lib_name]
        raise KeyError('did not find app or service with name {}'.format(app_or_lib_name))

    def get_apps_and_libs(self):
        return [app for app in self._document['apps'].values()] + [lib for lib in self._document['libs'].values()]

    def get_apps_and_services(self):
        return [app for app in self._document['apps'].values()] + [serv for serv in self._document['services'].values()]

    def get_apps_libs_and_services(self):
        return [app for app in self._document['apps'].values()] + \
               [lib for lib in self._document['libs'].values()] + \
               [serv for serv in self._document['services'].values()]
