#!/usr/bin/env python
"""A Pender plugin to lint Python files.

Capable of checking python files for syntax/lint errors and layout issues.

Configuration:
    use_python: Perform syntax checking with Python. Default True.
    use_pylint: Perform linting with PyLint. Default True.
    use_pep8:   Perform linting with pep8. Default True.
    use_pep257: Perform linting with pep257. Default True.
    use_yapf:   Perform code layout checking with yapf. Default True.

    max_line_length: Override tool max line length. Default unset.
    pylint_ignored_codes: Comma-separated list of pylint error codes to be
        ignored. Default: C0111 (redundant with pep257), C0303 (redundant with
        pep8), C0330 (conflicts with pep8), W0511 (xxx/fixme comments, should
        not veto commit).
    pep257_ignored_codes: Comma-separated list of pep257 error codes to be
        ignored. Default: D203 (conflicts with yapf).
    yapf_style: See `yapf --style` documentation.
"""

import os
import sys
import subprocess
import distutils.spawn

################
# Real constants
################
PENDER_OK = 0
PENDER_VETO = 10
PENDER_ERR = 1
DEBUG = True if 'PENDER_DEBUG' in os.environ else False


def check_lint(name, args, strip_first_line=False, output_is_error=False):
    """Call a Python linter and print problems that are found.

    strip_first_line:
        Strip the first line from output (for pylint)
    output_is_error:
        Assume output means lint failure (rather than non-zero exit) (for yapf)

    Return boolean success.
    """
    if DEBUG:
        print('check_linter', name, args, strip_first_line, output_is_error)
    success = True
    try:
        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    except OSError as e:
        print("Couldn't start %s, skipping ('%s')" % (name, e))
    else:
        stdout, _ = p.communicate()
        if p.returncode or (output_is_error and stdout.strip()):
            print("%s problems:" % name)
            lines = stdout.splitlines()
            if strip_first_line:
                lines = lines[1:]
            for line in lines:
                print('    {}'.format(line))
            success = False
    return success


def get_config():
    """Load config from argv & env."""
    config = {}
    config['real_file'] = sys.argv[2]
    config['temp_file'] = sys.argv[3]
    config['file_mime'] = sys.argv[4]
    config['use_python'] = os.environ.get("PENDER_use_python", True)
    config['use_pylint'] = os.environ.get("PENDER_use_pylint", True)
    config['use_pep8'] = os.environ.get("PENDER_use_pep8", True)
    config['use_pep257'] = os.environ.get("PENDER_use_pep257", True)
    config['use_yapf'] = os.environ.get("PENDER_use_yapf", True)
    # Max line length -- set to 0 to use each tool's default
    config['max_line_length'] = os.environ.get("PENDER_max_line_length", 0)
    # Ignored linter error codes.
    config['pylint_ignored_codes'] = os.environ.get(
        "PENDER_pylint_ignored_codes", ['C0303', 'C0330', 'W0511'])
    config['pep257_ignored_codes'] = os.environ.get(
        "PENDER_pep257_ignored_codes", ["D203"])
    config['yapf_style'] = os.environ.get("PENDER_yapf_style", "pep8")

    return config


def install():
    """Check depdencies are installed."""
    for app, hint in (('python', 'https://www.python.org/downloads/'),
                      ('pylint', 'http://www.pylint.org/#install'),
                      ('pep8', 'http://pep8.readthedocs.org/en/latest/'),
                      ('pep257', 'http://pep257.readthedocs.org/en/latest/'),
                      ('yapf', 'https://github.com/google/yapf'), ):
        if not distutils.spawn.find_executable(app):
            print("Couldn't find %s (hint: %s)" % (app, hint))


def check():
    """Run checks."""
    config = get_config()

    # Check the file is Python
    if not (config['real_file'].endswith('.py') or
            config['file_mime'] == 'text/x-python'):
        return PENDER_OK

    rc = PENDER_OK

    pylint_args = ['pylint', '--reports=no',
                   '--msg-template={line:3d}: {msg} ({msg_id})']
    if config['max_line_length']:
        pylint_args.append('--max-line-length=%s' % config['max_line_length'])
    pylint_args.append('-d=%s' % ','.join(config['pylint_ignored_codes']))
    pylint_args.append(config['temp_file'])
    pep8_args = ['pep8', '--format=%(row)3d,%(col)3d: %(text)s (%(code)s)']
    if config['max_line_length']:
        pep8_args.append('--max-line-length=%s' % config['max_line_length'])
    pep8_args.append(config['temp_file'])
    pep257_args = ['pep257']
    pep257_args.append('--ignore=%s' %
                       ','.join(config['pep257_ignored_codes']))
    pep257_args.append(config['temp_file'])

    linters = (
        (config['use_python'], {
            'name': 'python',
            'args': ('python', '-m', 'py_compile', config['temp_file'])
        }),
        (config['use_pylint'], {
            'name': 'pylint',
            'args': pylint_args,
            'strip_first_line': True
        }),
        (config['use_pep8'], {
            'name': 'pep8',
            'args': pep8_args
        }),
        (config['use_pep257'], {
            'name': 'pep257',
            'args': pep257_args
        }),
        (config['use_yapf'], {
            'name': 'yapf',
            'args': ('yapf', '-d', '--style=%s' % config['yapf_style'],
                     config['temp_file'])
        }),
    )  # yapf:disable

    for use, kwargs in linters:
        if use:
            if not check_lint(**kwargs):
                rc = PENDER_VETO

    return rc


def main():
    """Main program."""
    if sys.argv[1] == 'check':
        rc = check()
        sys.exit(rc)
    elif sys.argv[1] == 'install':
        install()
        sys.exit()
    else:
        print("Unknown action %s" % sys.argv[1])
        sys.exit(PENDER_ERR)

# MAIN PROGRAM STARTS HERE

if __name__ == '__main__':
    main()
