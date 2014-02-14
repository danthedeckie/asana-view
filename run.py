#!.virtualenv/bin/python
# -*- coding: utf-8 -*-
'''
    Simple run script

    Usage:

    ./run.sh
        (starts the development internal flask server.  FOR DEVELOPMENT ONLY!)

    ./run.sh waitress
        (starts the server running with the waitress production server)
'''

# Configuration Options:

__HOST__ = u'0.0.0.0'
__PORT__ = 5000
__THREADS__ = 3 # (for waitress, only)

# Initialise unicode:

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Load the app:

from app import app

# And start the correct server

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'waitress':
        print("'Production' Server with Waitress.")
        from waitress import serve
        serve(app, host=__HOST__, port=__PORT__, threads=__THREADS__)
    else:
        print("Starting Development Server...")
        app.run(host=__HOST__, port=__PORT__, debug = True)

