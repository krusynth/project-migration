#!/usr/bin/python

import requests
import json
import settings
from urlparse import urlparse, parse_qs


github_urls = {
  'repos': 'https://api.github.com/orgs/{}/repos'
}

gitlab_urls = {
  'projects': settings.GITLAB_DOMAIN + '/api/v3/projects/all',
  'repos': settings.GITLAB_DOMAIN + '/projects/{}/repository/tree'
}

# Get a list of all GitHub projects.
# This is so we don't create duplicates or overwrite anything.

print 'Getting projects from GitHub'

gh_projects = []

payload = {'access_token': settings.GITHUB_TOKEN}

# First off, how many pages do we have?

last_page = 0

# Get the first page.
head = requests.get(github_urls['repos'].format(settings.GITHUB_ORG), payload)
# Look for the last page link in the headers
links = head.headers['link'].split(',')
for link in links:
  link = link.split(';')
  if link[1].strip() == 'rel="last"':
    # Trim it for garbage, and get the data out.
    link_data = parse_qs(link[0].strip(' <>'))
    last_page = int(link_data['page'][0])

if last_page != 0:

  for page in range(1, last_page):

    new_payload = payload
    new_payload['page'] = page

    r = requests.get(github_urls['repos'].format(settings.GITHUB_ORG), new_payload)

    existing_projects = json.loads(r.text)

    for existing_project in existing_projects:
      gh_projects.append(existing_project['name'])

  print 'Found ' + str(len(gh_projects)) + ' projects'

else:
    print 'Didn\'t find any existing projects.'


# Get a list of all gitlab projects
print 'Getting GitLab projects'

payload = { 'private_token': settings.GITLAB_TOKEN, 'per_page': 1000}

r = requests.get(gitlab_urls['projects'], params=payload)

projects = json.loads(r.text)
# print r.text
for project in projects:
  print 'Project {}/{}'.format(project['namespace']['name'], project['name'])
