import cPickle

class Payload(object):
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def serialize(self):
        doc = {'fn': self.fn, 'args': self.args, 'kwargs': sorted(self.kwargs.items())}
        return cPickle.dumps(doc).encode('string_escape')

    @staticmethod
    def deserialize(doc):
        original_doc = cPickle.loads(doc.decode('string_escape'))
        return original_doc['fn'], original_doc['args'], dict(original_doc['kwargs'])
