from mock import patch, Mock

from dusty.memoize import memoized, reset_memoize_cache
from ..testcases import DustyTestCase

class TestMemoize(DustyTestCase):
    def setUp(self):
        super(TestMemoize, self).setUp()
        self.counter = 0
        @memoized
        def memoized_fn(kw1=None, kw2=None):
            self.counter += 1
            return self.counter
        self.memoized_fn = memoized_fn

    def test_memoize(self):
        self.memoized_fn()
        self.memoized_fn()
        self.assertEqual(self.counter, 1)

    def test_return_value(self):
        first = self.memoized_fn()
        second = self.memoized_fn()
        self.assertEqual(first, second)

    def test_cache_bust(self):
        self.memoized_fn()
        reset_memoize_cache()
        self.memoized_fn()
        self.assertEqual(self.counter, 2)

    def test_kwargs_order(self):
        self.memoized_fn(kw1=1, kw2=2)
        self.memoized_fn(kw2=2, kw1=1)
        self.assertEqual(self.counter, 1)
