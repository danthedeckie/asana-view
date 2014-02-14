#!.virtualenv/bin/python

import config
import requests
import json

BASE = 'https://app.asana.com/api/1.0/'

def list_to_dict(list_input, key='id'):
    ''' returns a dict, using the field 'key' from each item in list_input
        as the new dict key. '''
    d = {}
    for item in list_input:
        d[item[key]] = item
    return d

class AsanaError(Exception):
    pass

class SimpleAsana(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def _get_asana(self, url, *vargs, **kwargs):
        r = requests.get(BASE + url.format(*vargs),
                         params=kwargs,
                         auth=(self.api_key,''))
        try:
            print r.url
            return json.loads(r.text)['data']
        except KeyError as e:
            print r
            print r.url
            print r.text
            raise e

    def user(self, uid, **kwargs):
        return self._get_asana('users/{}', uid, **kwargs)

    def users(self, **kwargs):
        return self._get_asana('users', **kwargs)

    def teams(self, **kwargs):
        orgs = [o for o in self.organizations()
                if o['name'] != 'Personal Projects']
        if len(orgs) == 0:
            raise AsanaError('Not part of any organizations!')

        return self._get_asana('organizations/{}/teams', orgs[0]['id'], **kwargs)

    def workspaces(self, **kwargs):
        return self._get_asana('workspaces', **kwargs)

    def organizations(self, **kwargs):
        return [w for w in self._get_asana('workspaces',
                                           opt_fields='name,is_organization',
                                           **kwargs)
                if w['is_organization'] == True]

    def projects(self, **kwargs):
        return self._get_asana('projects', **kwargs)

    def project_tasks(self, project, **kwargs):
        return self._get_asana('projects/{}/tasks', project, **kwargs)

    def workspace_projects(self, workspace, **kwargs):
        return self._get_asana('workspaces/{}/projects', workspace, **kwargs)

    def workspace_tasks(self, workspace, **kwargs):
        return self._get_asana('workspaces/{}/tasks', workspace, **kwargs)

    def tasks(self, **kwargs):
        return self._get_asana('tasks', **kwargs)



if __name__ == '__main__':
    import config

    a = SimpleAsana(config.API_KEY)
    #print a.projects(opt_fields='name,team')
    teams = list_to_dict(a.teams(), 'id')

    projects = a.workspace_projects(config.WORKSPACE, opt_fields='name,team')

    for p in projects:
        p['team'] = teams[p['team']['id']]

    for p in [p for p in projects if p['team']['name'] == 'OMNIvision Videos']:
        print p['name']
        print '---------'
        tasks = a.project_tasks(p['id'], opt_fields='name,team,completed,due_on,completed_at,assignee,assignee_status')
        print tasks
