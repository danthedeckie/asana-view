import json
import traceback
from datetime import datetime

try:
    import re2 as re
except:
    import re

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
    return serial

class Config(object):
    ''' Flask-like 'config' object '''

    _config = {}

    def from_object(self, ob):
        self._config = ob

    def get(self, name, default):
        ''' get method for config... '''

        try:
            return getattr(self._config, name)
        except KeyError:
            return default
        except AttributeError:
            return default

    def __getitem__(self, key):
        return getattr(self._config, key)

    def __setitem__(self, key, value):
        return setattr(self._config, key, value)

class Application(object):
    ''' a very simple almost-flaskish application class '''

    def __init__(self):
        ''' initialise the routing... '''

        self.simpleroutes = {}
        self.reroutes = {}
        self.config = Config()

    def route(self, rule, **options):
        ''' a route decorator '''

        def decorator(function):
            self.simpleroutes[rule] = function
            return function
        return decorator

    def incoming(self, environ, start_response):
        ''' when requests come in, they get sent here '''

        # defaults:
        response_headers = [('Content-type', 'text/html')]
        status = '200 OK'

        try:
            resp = self.simpleroutes[environ['PATH_INFO']]
        except KeyError:
            status = '404 Not Found'
            data = "Sorry, this route was not defined.<br/>" \
                   "<pre>%s</pre>" % environ['PATH_INFO']
            
            start_response(status, response_headers)
            return [data]

        try:
            data = resp()
        except Exception as e:
            status = '500 Server Error'
            data = "Sorry, something went wrong!<br/>" \
                   "<pre>%s</pre>" % str(e)
            traceback.print_exc()

        if isinstance(data, dict):
            response_headers = [('Content-type', 'application/JSON')]
            data = json.dumps(data, default=json_serial)
        elif isinstance(data, tuple):
            status, content_type, data = data
            response_headers = [('Content-type', content_type)]

        start_response(status, response_headers)
        return [data]

    def __call__(self, environ, start_response):
        try:
            return self.incoming(environ, start_response)
        except Exception as e:
            start_response('500 Error', [('Content-type', 'text/plain')])
            return ['Error: %s' % e ]

def render_template(*vargs, **kwargs):
    return 'TEXT'

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer

    app = Application()

    @app.route('/')
    def index():
        return 'Hello World!'

    @app.route('/json')
    def j():
        return {"data":"stuff"}

    WSGIServer(('', 8000), app).serve_forever()
