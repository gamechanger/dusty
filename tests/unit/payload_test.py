import json

from ..testcases import DustyTestCase
from dusty.constants import VERSION
from dusty.payload import Payload, daemon_command, function_key, get_payload_function

@daemon_command
def _fn(*args, **kwargs):
    return args, kwargs

def _fn2(*args, **kwargs):
    return args, kwargs

class TestPayload(DustyTestCase):
    def setUp(self):
        super(TestPayload, self).setUp()
        self.test_payload = Payload(_fn, 'arg1', arg2='arg2value')
        self.serialized_payload = {'fn_key': function_key(_fn), 'client_version': VERSION, 'suppress_warnings': False, 'args': ('arg1',), 'kwargs': (('arg2', 'arg2value'),)}

    def test_serialize(self):
        result = json.loads(self.test_payload.serialize().decode('string_escape'))
        self.assertItemsEqual(result, self.serialized_payload)

    def test_deserialize(self):
        payload = Payload.deserialize(self.test_payload.serialize())
        fn_key, client_version, suppress_warnings, args, kwargs = payload['fn_key'], payload['client_version'], payload['suppress_warnings'], payload['args'], payload['kwargs']
        self.assertEqual(get_payload_function(fn_key), _fn)
        self.assertEqual(client_version, VERSION)
        self.assertEqual(set(args), set(('arg1',)))
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

    def test_get_payload_function_succeeds(self):
        self.assertEqual(_fn, get_payload_function(function_key(_fn)))

    def test_get_payload_function_raises(self):
        with self.assertRaises(RuntimeError):
            get_payload_function(function_key(_fn2))
