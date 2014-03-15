'''
    simplegcache.py - (C) 2014 Daniel Fairhead / OMNIvision
    MIT Licence.
    --------------------------------------------------------
    Very Simple gevent & python dict based object caching module.
    Don't try to use this for massively complex projects.  It is NOT
    "big data" scale, and will block and die.  Use Redis or something.
    --------------------------------------------------------

    The way this works is that you have a function that takes a long time
    to complete.  Say grabbing some data from a server somewhere.

    You then simply wrap calling that function in this module's 'get',
    specifying how long you want it to be cached for, etc.

    And, with luck, it works.

    >>> def slow_thing():
    >>>        sleep(12)
    >>>        return 42
    ...

    >>> simplegcache.get('the_answer', slow_thing, timeout=15)
    42

    Will return 42 (after some seconds).

    If you call it again:

    >>> simplegcache.get('the_answer', slow_thing, timeout=15)
    42

    is returned straight away.

    The default time that things live in the cache is 100 seconds.

    One important thing to note is that by default, if the cache has
    expired, then when get is called, it will straight away generate
    a new value.

    If you pass 'instant_expire=False' to simplegcache.get, then
    if the cache has expired, it will return the last value, and
    clear the cache for next time.  This can sometimes be helpful,
    if you have an application which can be turned off for quite
    a while, and you want it to boot up instantly, showing the old
    values, and then update once it's all happily running.



'''

from time import time
from gevent import spawn, Timeout
from gevent.coros import Semaphore

__CACHE__ = {}

__LOCK__ = Semaphore()

class Waiting(Exception):
    ''' When you're waiting for something to be set, longer than the
        timeout you specified '''
    pass


def get(key, func, cachetime=100, timeout=4, instant_expire=True):
    ''' get a value from the cache, or generate it if it's not there. '''

    need_to_run_again = False
    with __LOCK__:
        if key in __CACHE__:
            value, settime, waiting = __CACHE__[key]

            # and expire the old cache:
            if settime < time():
                del __CACHE__[key]
                need_to_run_again = True
        else:

            def background_getter():
                ''' this function runs in the background, and sets the
                    value in the cache to whatever the provided func wants.
                    It also handles the Locking, and raising exceptions, etc.
                '''
                try:
                    value = func()
                except:
                    del __CACHE__[key]
                    raise

                with __LOCK__:
                    __CACHE__[key] = value, time() + cachetime, None
                return value

            # so start it off:
            waiting = spawn(background_getter)

            # and set the __CACHE__ to say we are actually getting it...
            __CACHE__[key] = None, None, waiting

    if need_to_run_again and instant_expire:
        return get(key, func, cachetime, timeout, False)

    if waiting:

        with Timeout(timeout, Waiting):
            waiting.join()

        with __LOCK__:
            value, settime, waiting = __CACHE__[key]

        if waiting:
            raise Waiting()

    return value

if __name__ == '__main__':
    ####################################
    # Example usage code:

    from gevent import sleep

    def make_val(in_x):
        ''' simulate a very slow sqr function '''
        sleep(5)
        return in_x+in_x

    try:
        print get('answer', lambda: make_val(10))
    except Waiting:
        print '.'
        sleep(2)
        print get('answer', lambda: make_val(10), 15)


