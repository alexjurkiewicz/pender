# Pender

Pender is a Git pre-commit hook manager that lets you write checks in a simplified environment.

Three benefits over writing a real pre-commit hook yourself:

1. **Split your hook into multiple plugins** (per-language linting, site-specific checks, etc)
2. **Language-agnostic**. Plugins are executable files of any language.
3. **Simplified check environment**. Plugins are run per-file per-commit and Pender provides support for tricky things like partial commits (`git add -p`), reducing boilerplate code.

## Installation

Pender is intended to be copied in to your repository for all developers to use. It's written in Python 2 and works on OSX/Linux.

1. Copy `pre-commit.py`, `pre-commit.yaml` and `pre-commit-plugins/` to your repo's base directory.
2. Modify `pre-commit.yaml` as required.
3. Each developer can run `pre-commit.py` to install Pender into their local repository.

## Writing Pender Plugins

Pender plugins are executable files, and can be written in any language. Read [check_shell.sh](pre-commit-plugins/check_shell.sh) for a simple example.

Guidelines:

* Plugins are executed once per-file per-commit.
* Plugins are passed the following arguments:
  1. `check`
  2. Repository file path
  3. Temporary commit data file path
  4. MIME type (application/octet-stream if unknown)
* When checking a file's contents, use the temporary commit data file rather than the repository file. There may be changes in the repository file that are not part of the commit (eg, in case of `git add -p`).
* Plugins signal their decision by return code:
  * 0: OK the commit
  * 10: Veto the commit
  * 1: Internal plugin error (commit is OKed)
  * Any other return code: Reserved (currently interpreted as plugin error)
* Plugin stdout & stderr will always be shown.
* When the pre-commit hook is installed, all plugins in the plugin dir are run with the `install` argument only. This is a chance for plugins to make noise about missing dependencies or any other setup they require. Info should be output to stdout.

## Todo

* Multi-threaded plugin execution for speed
* Non-global installation
* More plugins
* Improve existing plugins
* Write language linter plugins in their language (eg check_ruby.py -> check_ruby.rb)

## License

This is free and unencumbered software released into the public domain.

## Help

Email me (alex@jurkiewi.cz) or open a Github issue.
