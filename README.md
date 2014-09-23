# PENDER

A lightweight git pre-commit hook wrapper.

## Overview

Pender is a git pre-commit hook that lets you write pre-commit hooks in a simplified environment. The big benefits over writing a real pre-commit hook yourself:

* Split your pre-commit hook into multiple files (for example: python script check, ruby script check, ...)
* Pender calls each plugin once per changed file, rather than once per commit.
* During pre-commit, a changed file's index copy may not match what is in the commit (eg, with `git add -p`). Pender always provides the real version for you.

## Installation

To install for just yourself:

1. Copy `pre_commit.py` to `.git/hooks/pre-commit` and update `PLUGIN_DIR` to `.git/hooks/pender-plugins/`
2. Copy `pender-plugins/` to `.git/hooks/pender-plugins/`

To make available for all repo users:

1. Copy `pre_commit.py` and `pender-plugins/` to somewhere in your repo
2. Update `PLUGINS_DIR` in `pre_commit.py` to point to `pender-plugins/` (the path is relative to the repository root)
3. Commit these files and push to your master repo
3. Each user should now run `./pre_commit.py` to install Pender locally

## Writing Pender Plugins

Pender plugins can be written in any language. Have a look at the examples in this repository.

The basic points for writing a Pender plugin are:

* The plugin is executed once per-file per-commit.
* The plugin is passed the following commandline parameters:
  * 1: File's repository path
  * 2: File's temporary commit data path
  * 3: File's MIME type (as reported by `file(1)`)
* When checking a file's contents, use the temporary commit data path rather than the repository path. There may be changes in the repository file that are not part of the commit (eg, in case of `git add -p`).
* Plugins signal their decision by return code:
  * 0: OK the commit
  * 10: Veto the commit
  * 1: Internal plugin error (commit is OKed)
  * Any other return code: Reserved (currently interpreted as plugin error)
* Plugin stdout & stderr will always be shown.
