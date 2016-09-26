# gitlab2github
A collection of tools to migrate existing GitLab repos into GitHub.


## lab2hub.py

This script reads the api info from `settings.py` to crawl a GitLab API for all
repos. It then creates a new repo of the same name on GitHub (skipping
duplicates). Last, it clones the old repo to a directory on the local
machine, adds the new github origin, and pushes it to GitHub.

## stats.py

Crawls the GitHub API to find out general info about projects and exports it as
a csv.  Returns the project name, the projects' license (if GitHub can detect
it), if the project has a README (again, if GitHub can detect it), and the
number of branches the project has.  Note that there is currently a bug where
the GitHub API only gets the branch count for the first 30 projects.

## findconfigs.py

A script to find all configuration files under a given directory path. Can be
passed an optional output file (with `-o outputfile`) to export the results to.

Configuration files are any file named with '*config.*' or '*settings.*'.

## deconfigure.py

Reads in a list of configuration files from a file (as output by
`findconfigs.py`), and creates a `.example.*` copy of each file.

It then reads each line of the new file looking for assignments (`:` or `=`),
and allows the user to choose a replacement line from the options of:

  * the original line or
  * the line with an empty string replacing the value assignment or
  * the original that the user can edit inline

The new file is then loaded into vim for the user to edit further.

The list of new files (and any files skipped because of duplicate names) are
output as a list.

## licensify.py

Searches a directory, or the children of a directory, for missing LICENSE files
and adds them.  Prompts the user to pick licenses for each directory. A quick
and easy way to bulk add licenses to repos.  You'll still need to manually
commit them, however - just in case.


## Other Tools

In addition to these tools, you'll probably want to use
[BFG](https://rtyley.github.io/bfg-repo-cleaner/) or [Clouseau](https://github.com/cfpb/clouseau) to clean your git history for
any secure credentials.
