#!.virtualenv/bin/python
'''
    cachedasana.py - part of 'asana-view' project
    -------------------------------------------------------------------
    Basic caching wrappers around SimpleAsana.

'''
#pylint: disable=star-args,too-few-public-methods

import simpleasana
from simplegcache import get, Waiting

class CachedAsana(object):
    ''' A version of SimpleAsana that caches all calls in the simplegcache '''

    def __init__(self, api_key):
        ''' load a SimpleAsana object... '''
        self.asana = simpleasana.SimpleAsana(api_key)

    def __getattr__(self, name):
        ''' when a function is requested, instead return a 'fake' function
            that checks in the cache first, before actually trying to run
            the real function '''

        def cached_or_real(*vargs, **kwargs):
            ''' this is returned, and then run. '''

            cachetime = kwargs.pop('cachetime', 300)
            cachename = name + str(hash(str(vargs))) + str(hash(str(kwargs)))

            def realfunc():
                ''' this is what actually gets called, if the value isn't
                    cached '''
                return getattr(self.asana, name)(*vargs, **kwargs)

            return get(cachename, realfunc, cachetime, 10)

        return cached_or_real

def get_project_tasks(*vargs, **kwargs):
    ''' cached version... '''

    cachetime = kwargs.pop('cachetime', 300)
    cachename = 'get_project_tasks' \
                + str(hash(str(vargs))) \
                + str(hash(str(kwargs)))

    try:
        return get(cachename,
                   lambda: simpleasana.get_project_tasks(*vargs, **kwargs),
                   cachetime, 10)
    except Waiting:
        return {"error": "waiting"}
