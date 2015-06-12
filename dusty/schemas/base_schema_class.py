from copy import deepcopy

# This is build on top of Schemer's functionality
class DustySchema(object):
    def __init__(self, schema, document):
        schema.validate(document)
        self._document = deepcopy(document)
        schema.apply_defaults(self._document)

    def __getitem__(self, name):
        return self._document[name]

    def __setitem__(self, key, value):
        self._document[key] = value

    def __delitem__(self, key):
        del self._document[key]

    def __contains__(self, key):
        return key in self._document

    def keys(self):
        return self._document.keys()

    def values(self):
        return self._document.values()
