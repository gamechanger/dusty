from copy import deepcopy

# This is build on top of Schemer's functionality
class DustySchema(object):
    def __init__(self, schema, document):
        schema.validate(document)
        self._document = deepcopy(document)
        schema.apply_defaults(self._document)

    def __getitem__(self, name):
        return self._document[name]
