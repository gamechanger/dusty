import functools
import pickle

from .payload import function_key

cache = {}

def memoized(fn):
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).  The cache lasts for the duration of each request.
    """
    @functools.wraps(fn)
    def memoizer(*args, **kwargs):
        key = function_key(fn) + pickle.dumps(args) + pickle.dumps(kwargs)
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return cache[key]
    return memoizer

def reset_memoize_cache():
    global cache
    cache = {}
