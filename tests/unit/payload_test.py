import cPickle

from ..testcases import DustyTestCase
from dusty.constants import VERSION
from dusty.payload import Payload

def _fn(*args, **kwargs):
    return args, kwargs

def _fn2(*args, **kwargs):
    return args, kwargs

class TestPayload(DustyTestCase):
    def setUp(self):
        super(TestPayload, self).setUp()
        self.test_payload = Payload(_fn, 'arg1', arg2='arg2value')
        self.serialized_payload = {'fn': _fn, 'client_version': VERSION, 'suppress_warnings': False, 'args': ('arg1',), 'kwargs': (('arg2', 'arg2value'),)}

    def test_serialize(self):
        result = cPickle.loads(self.test_payload.serialize().decode('string_escape'))
        self.assertItemsEqual(result, self.serialized_payload)

    def test_deserialize(self):
        payload = Payload.deserialize(self.test_payload.serialize())
        fn, client_version, suppress_warnings, args, kwargs = payload['fn'], payload['client_version'], payload['suppress_warnings'], payload['args'], payload['kwargs']
        self.assertEqual(fn, _fn)
        self.assertEqual(client_version, VERSION)
        self.assertEqual(args, ('arg1',))
        self.assertItemsEqual(kwargs, {'arg2': 'arg2value'})
        self.assertEqual(suppress_warnings, False)

    def test_equality_matches(self):
        self.assertEqual(self.test_payload, Payload(_fn, 'arg1', arg2='arg2value'))

    def test_equality_fails_bad_suppress(self):
        payload = Payload(_fn, 'arg1', arg2='arg2value')
        payload.suppress_warnings = True
        self.assertNotEqual(self.test_payload, payload)

    def test_equality_fails_bad_run_on_daemon(self):
        payload = Payload(_fn, 'arg1', arg2='arg2value')
        payload.run_on_daemon = False
        self.assertNotEqual(self.test_payload, payload)

    def test_equality_fails_bad_fn(self):
        self.assertNotEqual(self.test_payload, Payload(_fn2, 'arg1', arg2='arg2value'))

    def test_equality_fails_bad_args(self):
        self.assertNotEqual(self.test_payload, Payload(_fn, 'arg3', arg2='arg2value'))

    def test_equality_fails_bad_kwargs(self):
        self.assertNotEqual(self.test_payload, Payload(_fn, 'arg1', arg2='wrongvalue'))

    def test_equality_fails_wrong_class(self):
        self.assertNotEqual(self.test_payload, object())
