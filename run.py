#!.virtualenv/bin/python
# -*- coding: utf-8 -*-
'''
    Simple run script

    Usage:

    ./run.sh
'''

# Configuration Options:

__HOST__ = u'0.0.0.0'
__PORT__ = 5000
__THREADS__ = 3 # (for waitress, only)

from gevent.wsgi import WSGIServer
import gevent.monkey
gevent.monkey.patch_all()

# Initialise unicode:
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Load the app:

from app import app

# And start the correct server

if __name__ == '__main__':
    print("Gevent server")
    WSGIServer(('0.0.0.0', __PORT__), app).serve_forever()

