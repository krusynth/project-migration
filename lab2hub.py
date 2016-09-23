#!/usr/bin/python

import requests
import json
import settings
from urlparse import urlparse, parse_qs
from git import Repo

def getLastPage(link_header):
  links = link_header.split(',')
  for link in links:
    link = link.split(';')
    if link[1].strip() == 'rel="last"':
      # Trim it for garbage, and get the url params out.
      link_data = parse_qs(link[0].strip(' <>').split('?')[1])
      last_page = int(link_data['page'][0])
      return last_page
  return 0

github_urls = {
  'repos': 'https://api.github.com/orgs/{}/repos', # GET
  'create': 'https://api.github.com/orgs/{}/repos' # POST
}

gitlab_urls = {
  'projects': settings.GITLAB_DOMAIN + '/api/v3/projects/all',
  'repos': settings.GITLAB_DOMAIN + '/projects/{}/repository/tree'
}

# Get a list of all GitHub projects.
# This is so we don't create duplicates or overwrite anything.

print 'Getting projects from GitHub'

gh_projects = []

gh_payload = {'access_token': settings.GITHUB_TOKEN}

# First off, how many pages do we have?

# Get the first page.
head = requests.get(github_urls['repos'].format(settings.GITHUB_ORG), gh_payload)

# Look for the last page link in the headers
last_page = getLastPage(head.headers['link'])

if last_page != 0:

  for page in range(1, last_page + 1):

    new_payload = gh_payload
    new_payload['page'] = page

    r = requests.get(github_urls['repos'].format(settings.GITHUB_ORG), new_payload)

    existing_projects = json.loads(r.text)

    for existing_project in existing_projects:
      # print existing_project['name']
      gh_projects.append(existing_project['name'])

  print 'Found ' + str(len(gh_projects)) + ' projects'

else:
  print 'Didn\'t find any existing projects.'


# Get a list of all GitLab projects
print 'Getting GitLab projects'

gl_projects = []

gl_payload = {'private_token': settings.GITLAB_TOKEN}

# Get the first page.
head = requests.get(gitlab_urls['projects'], gl_payload)

# Look for the last page link in the headers
last_page = getLastPage(head.headers['link'])

if last_page != 0:

  for page in range(1, last_page + 1):

    new_payload = gl_payload
    new_payload['page'] = page

    r = requests.get(gitlab_urls['projects'], params=new_payload)

    projects = json.loads(r.text)

    for project in projects:
      # print '{}/{}'.format(project['namespace']['name'], project['name'])
      if project['name'] in gh_projects:
        pass
        # print 'Duplicate name - skipping'
        # print ''
      else:
        gl_projects.append(project)

  print 'Found ' + str(len(gl_projects)) + ' projects'

else:
  print 'Didn\'t find any projects.'

# Create the projects
for project in gl_projects:
  print '-- {}/{} --'.format(project['namespace']['name'], project['name'])

  print 'Creating on GitHub'

  repo_payload = {}
  repo_payload['name'] = project['name']
  repo_payload['private'] = True

  gh_repo = False

  r = requests.post(github_urls['repos'].format(settings.GITHUB_ORG), params=gh_payload, data=json.dumps(repo_payload))
  if r.status_code != 201:
    print '-> Failed: Error ' + str(r.status_code)
    print ''
    pass
    
  else:
    print 'Getting repo from GitLab'
    gh_repo = json.loads(r.text)

    repo_folder = settings.TEMP_FOLDER + project['name']
    
    repo = Repo.init(repo_folder)
    origin = repo.create_remote('origin',project['ssh_url_to_repo'])
    origin.fetch()
    try :
      origin.pull(origin.refs[0].remote_head)
    
    except AssertionError as error:
      print '-> Failed: Remotes problem'
      continue
    
    print 'Pushing repo to GitHub'
    gh_remote = repo.create_remote('gh',gh_repo['ssh_url'])
    push_result = gh_remote.push('--all')

    if len(push_result) is None:
      print '-> Failed'
    else:
      print 'Done'

    print ''
