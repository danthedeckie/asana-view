'''
    views.py - Part of 'asana-view' project.
    ---------------------------------------------------------------------
    Defines the actual views (routes).

'''

from flask import render_template, jsonify
import gevent
from gevent.pool import Pool
from app import app

if app.config.get('USECACHE', True):
    from cachedasana import CachedAsana as SimpleAsana, get_project_tasks
else:
    from simpleasana import SimpleAsana, get_project_tasks

@app.route('/')
@app.route('/index.html')
@app.route('/async_jobs')
def async_jobs():
    '''
        The main jobs/tasks overview HTML page.  Very basic, as essentially
        all it does is load the JS&CSS which does everything else.
    '''

    asana = SimpleAsana(app.config['API_KEY'])

    # Run both requests in parallel, which saves a little time:
    # (hey, we're in for a penny anyway in terms of gevent...)

    get_teams = gevent.spawn(asana.teams, as_type='dict')
    get_users = gevent.spawn(asana.users, as_type='dict', opt_fields='name,photo')

    gevent.joinall([get_teams, get_users], 10)
    teams = get_teams.value
    users = get_users.value

    return render_template('a_jobs.html', users=users, teams=teams)

@app.route('/api/jobs')
def api_jobs():
    '''
        The Main JSON view which gives a list of all tasks in all projects.
        This route uses a gevent pool go get all the project tasks in parallel
        (31 at a time), which makes life a lot quicker.  (Down to 7 or 8 seconds
        load time for us.)
    '''
    try:
        asana = SimpleAsana(app.config['API_KEY'])
        my_project_tasks = lambda p: get_project_tasks(app.config['API_KEY'], p)

        projects = asana.workspace_projects(
                                        app.config['WORKSPACE'],
                                        cachetime=4000,
                                        as_type='dict',
                                        opt_fields='name,team,archived,notes')
        all_tasks = []

        pool = Pool(31)

        lists = pool.map(my_project_tasks,
                         [p for p in projects if not p['archived']])


        for project_tasks in lists:
            all_tasks += project_tasks

        return jsonify({"tasks": all_tasks})

    except Exception as e: # pylint: disable=broad-except
        return str(e)
