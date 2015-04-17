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

## How Plugins Work

Pender plugins are executable files, and can be written in any language. Read [check_shell.sh](pre-commit-plugins/check_shell.sh) for a simple example.

You can configure plugins in `pre-commit.yaml`. See each plugin's header for help on its available options.

Information about writing plugins can be found in [PLUGINS.md](PLUGINS.md).

## Todo

* Multi-thread plugin execution for speed
* Improve existing plugins
* More plugins
* Non-global installation

## License

This is free and unencumbered software released into the public domain.

## Help

Email me (alex@jurkiewi.cz) or open a Github issue.
