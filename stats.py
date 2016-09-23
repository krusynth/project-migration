#!/usr/bin/python

# Exports a CSV of repo names, readme files, and the license of the project.

from __future__ import print_function
import requests
import json
import settings
from urlparse import urlparse, parse_qs
from git import Repo
import sys

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
  'license': 'https://api.github.com/repos/{}/{}', # GET
  'readme': 'https://api.github.com/repos/{}/{}/readme' # GET
}

gitlab_urls = {
  'projects': settings.GITLAB_DOMAIN + '/api/v3/projects/all',
  'repos': settings.GITLAB_DOMAIN + '/projects/{}/repository/tree'
}

# Get a list of all GitHub projects.

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

    headers = { 'Accept': 'application/vnd.github.drax-preview+json' }

    r = requests.get(github_urls['repos'].format(settings.GITHUB_ORG), new_payload, headers=headers)

    existing_projects = json.loads(r.text)

    for existing_project in existing_projects:
      # print(github_urls['license'].format(settings.GITHUB_ORG, existing_project['name']))
      repo_r = requests.get(github_urls['license'].format(settings.GITHUB_ORG, existing_project['name']), gh_payload, headers=headers)
      repo = json.loads(repo_r.text)

      # print existing_project['name']
      license = ''
      if repo.has_key('license') and repo['license'] is not None and \
        repo['license'].has_key('spdx_id') and repo['license']['spdx_id'] is not None:
        license = repo['license']['spdx_id']

      readme_r = requests.get(github_urls['readme'].format(settings.GITHUB_ORG, existing_project['name']), gh_payload, headers=headers)
      readme_data = json.loads(readme_r.text)

      readme = ''
      if readme_data.has_key('name'):
        readme = readme_data['name']

      print(','.join([existing_project['name'], license, readme]))

else:
  print('Didn\'t find any existing projects.', file=sys.stderr)
