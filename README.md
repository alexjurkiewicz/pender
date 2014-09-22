# PENDER

A lightweight git pre-commit hook wrapper.

## Overview

Pender is a git pre-commit hook that lets you write pre-commit hooks in a simplified environment. The big benefits over writing a real pre-commit hook yourself:

* Split your pre-commit hook into multiple files (for example: python script check, ruby script check, ...)
* Pender calls each child script once per changed file, rather than once per commit.
* During pre-commit, a changed file's index copy may not match what is in the commit (eg, with `git add -p`). Pender always provides the real version for you.

## Installation

To install for just yourself:

1. Copy `pre_commit.py` to `.git/hooks/pre-commit` and update `SCRIPTS_DIR` to `.git/hooks/pender-scripts/`
2. Copy `pender-scripts/` to `.git/hooks/pender-scripts/`

To make available for all repo users:

1. Copy `pre_commit.py` and `pender-scripts/` to somewhere in your repo
2. Update `SCRIPTS_DIR` in `pre_commit.py` to point to `pender-scripts/` (the path is relative to the repository root)
3. Commit these files and push to your master repo
3. Each user should now run `./pre_commit.py` to install Pender locally

## Writing Pender Scripts

Pender scripts can be written in any language. Have a look at the examples in this repository.

The basic points for writing a Pender script are:

* The script is called once per-file per-commit: if a commit includes three files, the script will be called three times.
* The script is passed the following variables:
  * 1: Repository path
  * 2: Temporary commit data path
  * 3: File's MIME type (as reported by `file(1)`)
* When checking a file's contents, use the temporary commit data path rather than the repository path. There may be changes in the repository file that are not part of the commit (eg, in case of `git add -p`).
* Scripts signal their decision by return code:
  * 0: OK the commit
  * 10: Veto the commit
  * 1: Internal script error (commit is OKed)
  * Any other return code: Reserved (currently interpreted as script error)
* Script's stdout & stderr will always be shown.
