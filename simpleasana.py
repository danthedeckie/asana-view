#!.virtualenv/bin/python
'''
    simpleasana.py - part of 'asana-view' project
    -------------------------------------------------------------------
    A very basic read-only api for the bits of asana that we want to read.
'''

import requests
import json
from datetime import datetime, timedelta

BASE = 'https://app.asana.com/api/1.0/'

def list_to_dict(list_input, key='id'):
    ''' returns a dict, using the field 'key' from each item in list_input
        as the new dict key. '''

    new_dict = {}

    for item in list_input:
        new_dict[item[key]] = item

    return new_dict

class AsanaError(Exception):
    ''' An error with talking to Asana '''
    pass

class SimpleAsana(object):
    ''' Basic API object.  '''

    def __init__(self, api_key):
        ''' set up the API_KEY '''
        self.api_key = api_key

    def _get_asana(self, url, *vargs, **kwargs):
        ''' send a request to asana. '''

        req = requests.get(BASE + url.format(*vargs),
                           params=kwargs,
                           auth=(self.api_key, ''))
        try:
            print req.url
            return json.loads(req.text)['data']
        except KeyError as e:
            print req
            print req.url
            print req.text
            raise AsanaError(req.text + ':' + str(e))

    def user(self, uid, **kwargs):
        ''' get details about a user '''

        return self._get_asana('users/{}', uid, **kwargs)

    def users(self, as_type=None, **kwargs):
        ''' get details about users '''

        if as_type == 'dict':
            return list_to_dict(self.users(**kwargs))

        return self._get_asana('users', **kwargs)

    def teams(self, as_type=None, **kwargs):
        ''' get details about all teams in this organisation '''

        if as_type == 'dict':
            return list_to_dict(self.teams(**kwargs))

        orgs = [org for org in self.organizations()
                if org['name'] != 'Personal Projects']

        if len(orgs) == 0:
            raise AsanaError('Not part of any organizations!')

        return self._get_asana('organizations/{}/teams',
                               orgs[0]['id'], **kwargs)

    def workspaces(self, **kwargs):
        ''' get list of all available workspaces '''

        return self._get_asana('workspaces', **kwargs)

    def organizations(self, **kwargs):
        ''' get a list of all available workspaces '''

        return [wksp for wksp in self._get_asana('workspaces',
                                           opt_fields='name,is_organization',
                                           **kwargs)
                if wksp['is_organization'] == True]

    def projects(self, as_type=None, **kwargs):
        ''' get a list of all available projects '''

        if as_type == 'dict':
            return list_to_dict(self.projects(**kwargs))

        return self._get_asana('projects', **kwargs)

    def project_tasks(self, project, **kwargs):
        ''' get a list of all tasks within a project '''

        return self._get_asana('projects/{}/tasks', project, **kwargs)

    def workspace_projects(self, workspace, **kwargs):
        ''' get a list of all projects within a workspace '''

        return self._get_asana('workspaces/{}/projects', workspace, **kwargs)

    def workspace_tasks(self, workspace, **kwargs):
        ''' get a list of all tasks within a workspace '''

        # requires other options, such as assignee...

        return self._get_asana('workspaces/{}/tasks', workspace, **kwargs)

    def tasks(self, **kwargs):
        ''' get tasks, with whatever options you ask for '''

        return self._get_asana('tasks', **kwargs)


def get_project_tasks(api_key, project):
    '''
        Given a Project (p), return a list of all tasks in that project,
        re-parsed, with time_class, etc.
    '''

    asana = SimpleAsana(api_key)
    now = datetime.now()
    soon = now + timedelta(days=6)

    raw_tasks = asana.project_tasks(project['id'],
                                    cachetime=600,
                                    opt_fields='name,completed,due_on,'
                                               'completed_at,assignee,'
                                               'assignee_status')

    tasks = []

    for task in [t for t in raw_tasks if not t['completed']]:
        if task['assignee']:
            if task['due_on']:
                task['due_on'] = datetime.strptime(task['due_on'], "%Y-%m-%d")
                if task['due_on'] < now:
                    task['time_class'] = 'past'
                elif task['due_on'] < soon:
                    task['time_class'] = 'soon'
                else:
                    task['time_class'] = 'sometime'
                task['project'] = project

                tasks.append(t)

    return tasks
