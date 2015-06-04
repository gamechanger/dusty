import cPickle

from ..testcases import DustyTestCase
from dusty.payload import Payload

def _fn(*args, **kwargs):
    return args, kwargs

def _fn2(*args, **kwargs):
    return args, kwargs

class TestPayload(DustyTestCase):
    def setUp(self):
        super(TestPayload, self).setUp()
        self.test_payload = Payload(_fn, 'arg1', arg2='arg2value')
        self.serialized_payload = {'fn': _fn, 'args': ('arg1',), 'kwargs': (('arg2', 'arg2value'),)}

    def test_serialize(self):
        result = cPickle.loads(self.test_payload.serialize().decode('string_escape'))
        self.assertItemsEqual(result, self.serialized_payload)

    def test_deserialize(self):
        fn, args, kwargs = Payload.deserialize(self.test_payload.serialize())
        self.assertEqual(fn, _fn)
        self.assertEqual(args, ('arg1',))
        self.assertItemsEqual(kwargs, {'arg2': 'arg2value'})

    def test_equality_matches(self):
        self.assertEqual(self.test_payload, Payload(_fn, 'arg1', arg2='arg2value'))

    def test_equality_fails_bad_fn(self):
        self.assertNotEqual(self.test_payload, Payload(_fn2, 'arg1', arg2='arg2value'))

    def test_equality_fails_bad_args(self):
        self.assertNotEqual(self.test_payload, Payload(_fn, 'arg3', arg2='arg2value'))

    def test_equality_fails_bad_kwargs(self):
        self.assertNotEqual(self.test_payload, Payload(_fn, 'arg1', arg2='wrongvalue'))

    def test_equality_fails_wrong_class(self):
        self.assertNotEqual(self.test_payload, object())
