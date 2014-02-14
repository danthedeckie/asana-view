from flask import render_template, url_for, request
from simpleasana import SimpleAsana, list_to_dict
from app import app
from sqlcache import SqliteCache

class CachedAsana(object):
    def __init__(self, api_key, db_name):
        self.a = SimpleAsana(api_key)
        self.c = SqliteCache(db_name)

    def __getattr__(self, name):
        ''' when a function is requested, instead return a 'fake' function
            that checks in the cache first, before actually trying to run
            the real function '''

        def cached_or_real(*vargs, **kwargs):
            cachename = name + str(hash(str(vargs))) + str(hash(str(kwargs)))
            cached = self.c.get(cachename)
            if cached:
                return cached
            else:
                real = getattr(self.a, name)(*vargs, **kwargs)
                self.c.set(cachename, real, 300)
                return real

        return cached_or_real

@app.route('/')
@app.route('/index.html')
def index():

    a = CachedAsana(app.config['API_KEY'], 'cache.db')

    teams = list_to_dict(a.teams())

    users = list_to_dict(a.users(opt_fields='name,photo'))
    print users

    projects = a.workspace_projects(app.config['WORKSPACE'], opt_fields='name,team,archived,notes')

    for p in [p for p in projects if not p['archived']]:
        p['team'] = teams[p['team']['id']]
        if p['team']['name'] == 'OMNIvision Videos':
            p['tasks'] = a.project_tasks(p['id'], opt_fields='name,completed,due_on,completed_at,assignee,assignee_status')

    return render_template('index.html',
        users=users,
        projects=[p for p in projects if 'tasks' in p])

@app.route('/project/<int:pid>')
def project(pid):
    a = asana.AsanaAPI(app.config['API_KEY'])
    return render_template('project.html')

