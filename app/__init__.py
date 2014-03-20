# -*- coding: utf-8 -*-
'''
    The basic application definition
'''


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import simpleasana
from espressocup import Application
import config

app = Application(__name__) # pylint: disable=invalid-name
app.config.from_object(config)

# Check that everything has been set up that we need (API_KEY and WORKSPACE)

def sanity_check():
    ''' run basic sanity check's on config values, prompt for required bits '''
    if not app.config.get('API_KEY', None):
        print 'You need to set the API_KEY in config.py!'
        exit(1)

    if not app.config.get('WORKSPACE', None):
        print 'You have not set your config.py WORKSPACE variable! ' \
              '(Loading default)...'

        asana = simpleasana.SimpleAsana(app.config['API_KEY'])
        workspaces = asana.workspaces()

        app.config['WORKSPACE'] = str(workspaces[0]['id'])

        print 'Using Workspace: %i (%s)' \
              % (workspaces[0]['id'], workspaces[0]['name'])

        print 'Set WORKSPACE="%i" in your config.py to boot quicker.' \
                % workspaces[0]['id']

        print 'All options:'
        print workspaces

sanity_check()

from app import views
