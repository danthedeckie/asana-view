from flask import render_template, url_for, request, json
from simpleasana import SimpleAsana, list_to_dict
from app import app
from sqlcache import SqliteCache
from datetime import datetime, timedelta


class CachedAsana(object):
    def __init__(self, api_key, db_name):
        self.a = SimpleAsana(api_key)
        self.c = SqliteCache(db_name)

    def __getattr__(self, name):
        ''' when a function is requested, instead return a 'fake' function
            that checks in the cache first, before actually trying to run
            the real function '''

        def cached_or_real(*vargs, **kwargs):
            cachetime = kwargs.pop('cachetime', 300)
            cachename = name + str(hash(str(vargs))) + str(hash(str(kwargs)))
            cached = self.c.get(cachename)
            if cached:
                return cached
            else:
                real = getattr(self.a, name)(*vargs, **kwargs)
                self.c.set(cachename, real, cachetime)
                return real

        return cached_or_real

@app.route('/')
@app.route('/index.html')
def index():

    if not app.config['API_KEY']:
        return '<h1>You need to set an API_KEY in your config.py.</h1>'

    a = CachedAsana(app.config['API_KEY'], 'cache.db')

    teams = a.teams(as_type='dict',cachetime=15000)

    users = a.users(opt_fields='name,photo', as_type='dict', cachetime=6000)

    if not 'WORKSPACE' in app.config:
        return '<h1>Workspace not specified.</h1>' + \
            json.dumps(a.workspaces())

    projects = a.workspace_projects(app.config['WORKSPACE'], cachetime=4000,
                                    opt_fields='name,team,archived,notes')

    for p in [p for p in projects if not p['archived']]:
        p['team'] = teams[p['team']['id']]
        if p['team']['name'] == app.config['TEAM_NAME']:
            p['tasks'] = a.project_tasks(p['id'], cachetime=600,
                                         opt_fields='name,completed,'
                                                    'due_on,completed_at,'
                                                    'assignee,assignee_status')

    return render_template('index.html',
        users=users,
        projects=[p for p in projects if 'tasks' in p])

@app.route('/jobs')
def jobs():
    now = datetime.now()

    a = CachedAsana(app.config['API_KEY'],'cache.db')

    teams = a.teams(as_type='dict', cachetime=15000)
    users = a.users(as_type='dict', opt_fields='name,photo', cachetime=6000)

    projects = a.workspace_projects(app.config['WORKSPACE'], cachetime=4000,
                                    as_type='dict',
                                    opt_fields='name,team,archived,notes')

    tasks=[]

    for p in [p for p in projects if not p['archived']]:
        ts = a.project_tasks(p['id'], cachetime=600,
                             opt_fields='name,completed,due_on,completed_at,'
                                        'assignee,assignee_status')
        for t in [t for t in ts if not t['completed']]:
            if t['assignee']:
                if t['due_on']:
                    t['due_on'] = datetime.strptime(t['due_on'],"%Y-%m-%d")
                    if t['due_on'] < now:
                        t['time_class'] = 'past'
                    elif t['due_on'] < now + timedelta(days=2):
                        t['time_class'] = 'soon'
                    else:
                        t['time_class'] = 'sometime'
                    t['project'] = p

                    tasks.append(t)
        #tasks += ts

    return render_template('jobs.html',
                            users=users,
                            tasks=tasks)
