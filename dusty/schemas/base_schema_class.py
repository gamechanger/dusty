from copy import deepcopy
import collections


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


# This is build on top of Schemer's functionality
class DustySchema(BaseMutable):
    def __init__(self, schema, document):
        schema.validate(document)
        self._document = deepcopy(document)
        super(DustySchema, self).__init__(deepcopy(document))
        schema.apply_defaults(self._document)


class DustySpecs(BaseMutable):
    def get_app_or_lib(self, app_or_lib_name):
        if app_or_lib_name in self._document['apps']:
            return self._document['apps'][app_or_lib_name]
        elif app_or_lib_name in self._document['libs']:
            return self._document['libs'][app_or_lib_name]
        raise KeyError('did not find app or service with name {}'.format(app_or_library_name))

    def get_apps_and_libs(self):
        return [app for app in self._document['apps'].values()] + [lib for lib in self._document['libs'].values()]
