#!/usr/bin/python

# Takes a file containing a list of config files.
# Tries to create an .example.* version of each file.
# Looks for any string that's an assignment and asks if it should be cleared.
# Opens the file in vim for final review.
# Outputs the list of new files

import sys
import os
import re
import gnureadline as readline
import subprocess

# http://stackoverflow.com/questions/5403138/how-to-set-a-default-string-for-raw-input
def rlinput(prompt, prefill=''):
  def hook():
    readline.insert_text(prefill)

  readline.set_startup_hook(hook)
  try:
    return raw_input(prompt)
  finally:
    readline.set_startup_hook()

if len(sys.argv) < 2:
  print 'Please specify a file to read.'
  exit()

new_files = []
problem_files = []

assign_pattern = re.compile(r'([:=])(\s*)([\'"])(.*?)(\3)')

# Get each line from our file of config files.
with open(sys.argv[1]) as f:
  for filename in f:
    filename = filename.strip()
    # copy each file.
    fileparts = filename.split('.')
    example_file = '.'.join(fileparts[0:-1]) + '.example.' + fileparts[-1]

    if os.path.isfile(example_file):
      print example_file + ' exists! Skipping.'
      problem_files.append(filename)
      continue

    lines = []

    with open(filename) as config_file:
      print 'Editing ' + example_file
      print ''

      for line in config_file:
        line = line.rstrip()
        if re.match(r'^\s*#', line) == None and re.search(r':|=', line):
          edited_line = assign_pattern.sub(r'\1\2\3\3', line)
          print 'Old: ' + line
          print 'New: ' + edited_line

          yesno = raw_input('N(ew) / E(dit) / Old (any key) ? ').strip()
          if yesno == 'N':
            lines.append(edited_line)
          elif yesno == 'E':
            edited_line = rlinput('Edit: ', prefill=edited_line)
            lines.append(edited_line)
          else:
            lines.append(line)

          print ''
        else:
          lines.append(line)

    with open(example_file, 'w+') as new_file:
      for line in lines:
        new_file.write(line + "\n")

    # Open the example file for a final review.
    p = subprocess.Popen(('vim', example_file))
    p.wait()

    new_files.append(example_file)

    print 'saved.'
    print ''

print 'done.'
print ''

print '-- New Files --'
print ''
for file in new_files:
  print file
print ''

print '-- Problem Files --'
print ''
for file in problem_files:
  print file
print ''



