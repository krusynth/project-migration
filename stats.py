#!/usr/bin/python

# Exports a CSV of repo names, readme files, and the license of the project.

from __future__ import print_function
import requests
import json
import settings
from urlparse import urlparse, parse_qs

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
  'readme': 'https://api.github.com/repos/{}/{}/readme', # GET
  'branches': 'https://api.github.com/repos/{}/{}/branches' # GET
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

  print('Name,License,Readme?,Branches Count')

  for page in range(1, last_page + 1):

    new_payload = gh_payload
    new_payload['page'] = page

    headers = { 'Accept': 'application/vnd.github.drax-preview+json' }

    r = requests.get(github_urls['repos'].format(settings.GITHUB_ORG), new_payload, headers=headers)

    existing_projects = json.loads(r.text)

    for existing_project in existing_projects:
      # print('-- ' + existing_project['name'] + ' --')

      repo_r = requests.get(github_urls['license'].format(settings.GITHUB_ORG, existing_project['name']), gh_payload, headers=headers)
      repo = json.loads(repo_r.text)

      license = ''
      if repo.has_key('license') and repo['license'] is not None and \
        repo['license'].has_key('spdx_id') and repo['license']['spdx_id'] is not None:
        license = repo['license']['spdx_id']

      readme_r = requests.get(github_urls['readme'].format(settings.GITHUB_ORG, existing_project['name']), gh_payload, headers=headers)
      readme_data = json.loads(readme_r.text)

      readme = ''
      if readme_data.has_key('name'):
        readme = str(readme_data['name'])

      branches_headers = { 'Accept': 'application/vnd.github.loki-preview+json'}
      branches_payload = gh_payload
      branches_payload['per_page'] = 100

      branches_r = requests.get(github_urls['branches'].format(settings.GITHUB_ORG, existing_project['name']), gh_payload, headers=branches_headers)
      branches_data = json.loads(branches_r.text)

      ### After 30 queries, branches_data is [] for all subsequent requests !!!

      branch_count = '0'
      if branches_data:
        branch_count = str(len(branches_data))

      print(','.join([existing_project['name'], license, readme, branch_count]))

else:
  print('Didn\'t find any existing projects.', file=sys.stderr)
