#!/usr/bin/python

# Finds files named settings or config in folders and allows the user to
# review all of them for revealed passwords. Outputs a list of flagged files.

from __future__ import print_function
import glob2
import sys
import readline
import pydoc
import argparse
import datetime

# The licenses that we have copies of here.
LICENSES = ['GPL3', 'MIT', 'CC0', 'Apache2', 'None']
REQUIRES_NAME = ['MIT', 'Apache2']

parser = argparse.ArgumentParser(description='Finds license files, and lets the user add missing ones to repos.')
parser.add_argument('directory', help='the directory to search.')
parser.add_argument('-n', dest='name', help='The owner name for the copyright')
# parser.add_argument('-o', dest='outfile', type=argparse.FileType('w'), help='file to write the results to.')
parser.add_argument('-l', dest='license', help='license to use for all matching directories.', choices=LICENSES)
parser.add_argument('-r', dest='recursive', action='store_true', help='search the children of the directory, not the directory itself.')
parser.add_argument('--check-only', dest='check_only', action='store_true', help='only check for missing licenses and output a list.')
parser.add_argument('--filename', dest='license_filename', help='the filename to use for the license file.')

args = parser.parse_args()
name = args.name or ''
year = str(datetime.datetime.now().year)
license_name = args.license_filename or 'LICENSE'

project_dir = args.directory.strip().rstrip('/') + '/'
if args.recursive :
  project_dir += '*/'

print('Searching ' + project_dir)

missing_licenses = []

directories = glob2.glob(project_dir)
for directory in directories:
  licenses = glob2.glob(directory + '/LICENSE*')
  if len(licenses) == 0:
    missing_licenses.append(directory)

# If we're only checking, just spit out our list of directories and quit.
if args.check_only:
  for directory in missing_licenses:
    print(directory)
  exit()

print('{} missing licenses.'.format(str(len(missing_licenses))))
print('')

if len(missing_licenses) == 0:
  exit()

# Create a dictionary to hold our results
license_map = dict( (key, []) for key in LICENSES )

for directory in missing_licenses:
  print(directory)
  prompt = ', '.join(LICENSES) + ' ? '
  if args.license:
    prompt += ' [Enter: ' + args.license + '] '

  value = ''
  while value == '':
    value = raw_input(prompt).strip()
    if value == '' and args.license:
      value = args.license
    if value not in LICENSES:
      value = ''

  license_map[value].append(directory)

for license,values in license_map.iteritems():
  if license == 'None' or len(values) == 0:
    continue

  print('-- ' + license + ' --')
  print('')

  # Make sure we have a name if we need one.
  if license in REQUIRES_NAME and name == '':
    while name == '':
      name = raw_input('Please enter the copyright owner\'s name for the license: ')

  license_file = './licenses/{}.txt'.format(license)
  contents = ''
  with open( license_file ) as f:
    contents = f.read()

  # Swap our info into the license template.
  contents = contents.replace('[name]', name)
  contents = contents.replace('[year]', year)

  for project_directory in values:
    print(project_directory + license_name)

    with open( project_directory + license_name, 'w+' ) as f:
      f.write(contents)

  print('')
