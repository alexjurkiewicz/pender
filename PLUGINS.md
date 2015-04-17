## Writing Pender Plugins

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
* Plugin configuration works as follows:
  * Configuration can be set in `pre-commit.yaml` in the 'plugins' section under a key with the same name as the file without extension (eg `check_python`).
  * The keys in this area will be set in the plugin's environment as `PENDER_key = val`. If a value is a sequence, the sequence items will be comma-separated. For example, the following configuration file:
```yaml
plugins:
    check_python:
        use_yapf: false
        pylint_ignored_codes:
            - C0303
            - W0511
```
Translates to the following environment variables when running `check_python.py`:
    * `PENDER_use_yapf=false`
    * `PENDER_pylint_ignored_codes=C0303,W0511`
