from copy import deepcopy

# This is build on top of Schemer's functionality
class DustySchema(object):
    def __init__(self, schema, document):
        schema.validate(document)
        import logging
        logging.error(document)
        self._document = deepcopy(document)
        schema.apply_defaults(self._document)
        logging.error(self._document)

    def __getitem__(self, name):
        return self._document[name]

    def __contains__(self, key):
        return key in self._document

    def keys(self):
        return self._document.keys()

    def values(self):
        return self._document.values()
