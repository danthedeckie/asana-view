from flask import render_template, url_for, request, json, jsonify
from simpleasana import SimpleAsana, list_to_dict
from app import app
from datetime import datetime, timedelta
import gevent
from gevent.pool import Pool

def get_project_tasks(p):
    a = SimpleAsana(app.config['API_KEY'])
    now = datetime.now()
    soon = now + timedelta(days=6)

    ts = a.project_tasks(p['id'], cachetime=600,
                         opt_fields='name,completed,due_on,completed_at,'
                                    'assignee,assignee_status')

    tasks = []

    for t in [t for t in ts if not t['completed']]:
            if t['assignee']:
                if t['due_on']:
                    t['due_on'] = datetime.strptime(t['due_on'],"%Y-%m-%d")
                    if t['due_on'] < now:
                        t['time_class'] = 'past'
                    elif t['due_on'] < soon:
                        t['time_class'] = 'soon'
                    else:
                        t['time_class'] = 'sometime'
                    t['project'] = p

                    tasks.append(t)

    return tasks

@app.route('/')
@app.route('/index.html')
@app.route('/async_jobs')
def async_jobs():
    a = SimpleAsana(app.config['API_KEY'])

    t = gevent.spawn( a.teams, as_type='dict' ) 
    u = gevent.spawn( a.users, as_type='dict', opt_fields='name,photo')

    gevent.joinall([t,u], 10)
    teams = t.value
    users = u.value

    return render_template('a_jobs.html', users=users, teams=teams)

@app.route('/api/jobs')
def api_jobs():
    try:
        now = datetime.now()

        a = SimpleAsana(app.config['API_KEY'])

        projects = a.workspace_projects(app.config['WORKSPACE'], cachetime=4000,
                                        as_type='dict',
                                        opt_fields='name,team,archived,notes')
        tasks=[]

        pool = Pool(31)

        lists = pool.map(get_project_tasks,
                         [p for p in projects if not p['archived']])


        for ts in lists:
            tasks += ts

        return jsonify({"tasks": tasks})
    except Exception as e:
        return str(e)
