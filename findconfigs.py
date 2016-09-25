#!/usr/bin/python

# Finds files named settings or config in folders and allows the user to
# review all of them for revealed passwords. Outputs a list of flagged files.

# TODO:

from __future__ import print_function
import glob2
import sys
import readline
import pydoc
import argparse

parser = argparse.ArgumentParser(description='Finds configuration files, and lets the user review and flag them.')
parser.add_argument('directory', help='the directory to search. (Recursive)')
parser.add_argument('-o', dest='outfile', type=argparse.FileType('w'), help='file to write the results to.')

args = parser.parse_args()

confdir = args.directory.strip().rstrip('/')

print('Searching ' + confdir)

files = glob2.glob('{}/**/*settings.*'.format(confdir))
files.extend(glob2.glob('{}/**/*config.*'.format(confdir)))

print('{} config files found.'.format(str(len(files))))
print('')

if len(files) == 0:
  exit()

raw_input('Press RETURN to begin reviewing these files. Press q to exit the review tool.')

flagged_files = []
for file in files:
  print('File ', file)
  with open(file, 'r') as f:
    pydoc.pager(f.read())

  yesno = raw_input('Flag this file? Y/N: ')
  if yesno == 'Y':
    flagged_files.append(file)

print('')
print('{} config files flagged.'.format(str(len(flagged_files))))
print('')

if len(flagged_files) == 0:
  exit()

if args.outfile:
  print('Writing output to ' + args.outfile.name)
  with args.outfile as f:
    for file in flagged_files:
      f.write(file + "\n")

else:
  print('-- Files --')
  print('')

  for file in flagged_files:
    print(file)

  print('')
  print('-- End Files --')
  print('')
