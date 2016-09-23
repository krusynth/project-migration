#!/usr/bin/python

# Finds files named settings or config in folders and allows the user to
# review all of them for revealed passwords. Outputs a list of flagged files.

from __future__ import print_function
import glob2
import sys
import readline

import pydoc

if len(sys.argv) <2:
  print('You must specify a directory to search.', file=sys.stderr)
  exit()

gitdir = sys.argv[1].strip().rstrip('/')

files = glob2.glob('{}/**/*settings.*'.format(gitdir))
files.extend(glob2.glob('{}/**/*config.*'.format(gitdir)))

flagged_files = []

print('{} config files found.'.format(str(len(files))))
print('')
raw_input('Press RETURN to begin reviewing these files. Press q to exit the review tool.')

for file in files:
  print('File ', file)
  with open(file, 'r') as f:
    pydoc.pager(f.read())

  yesno = raw_input('Flag this file? Y/N: ')
  if yesno == 'Y':
    flagged_files.append(file)

print('')
print('{} config files found.'.format(str(len(flagged_files))))
print('')
print('-- Files --')
print('')

for file in flagged_files:
  print(file)

print('')
print('-- End Files --')
print('')
