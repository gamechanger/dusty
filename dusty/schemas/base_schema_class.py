from copy import deepcopy
import collections

# This is build on top of Schemer's functionality
class DustySchema(collections.MutableMapping):
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

    def __iter__(self):
        return iter(self._document)

    def __len__(self):
        return len(self._document)

    def keys(self):
        return self._document.keys()

    def values(self):
        return self._document.values()


class DustySpecs(collections.MutableMapping):
    def __init__(self, specs_dict):
        self._specs_dict = specs_dict

    def __getitem__(self, name):
        return self._specs_dict[name]

    def __setitem__(self, key, value):
        self._specs_dict[key] = value

    def __delitem__(self, key):
        del self._specs_dict[key]

    def __contains__(self, key):
        return key in self._specs_dict

    def __iter__(self):
        return iter(self._specs_dict)

    def __len__(self):
        return len(self._specs_dict)

    def keys(self):
        return self._specs_dict.keys()

    def values(self):
        return self._specs_dict.values()
