#!/usr/bin/env python
"""A Pender plugin to lint Python files."""

import os
import sys
import subprocess
import distutils.spawn

####################
# USER CONFIGURATION
####################
# Which linters should we use?
USE_PYTHON = True
USE_PYLINT = True
USE_PEP8 = True
USE_PEP257 = True
USE_YAPF = True
# Max line length -- set to 0 to use each tool's default
MAX_LINE_LENGTH = 0
# Ignored linter error codes.
PYLINT_IGNORED_CODES = (
    'C0111',  # missing docstring -- redundant with pep257
    'C0303',  # trailing whitespace -- redundant with pep8
    'C0330',  # wrong continued indentation -- conflicts with pep8
    'W0511',  # xxx/fixme etc -- should not veto commit
)
PEP257_IGNORED_CODES = (
    'D203',  # Expected 1 blank line *before* class docstring -- yapf conflict
)
# yapf coding style, could be 'google' or 'chromium'
YAPF_STYLE = 'pep8'

################
# Real constants
################
PENDER_OK = 0
PENDER_VETO = 10
PENDER_ERR = 1
DEBUG = True if 'PENDER_DEBUG' in os.environ else False


def check_linter(name, args, strip_first_line=False, output_is_error=False):
    """Call a Python linter and print problems that are found.

    strip_first_line:
        Strip the first line from output (for pylint)
    output_is_error:
        Assume output means lint failure (rather than non-zero exit) (for yapf)

    Return boolean success.
    """
    if DEBUG:
        print 'check_linter', name, args, strip_first_line, output_is_error
    success = True
    try:
        p = subprocess.Popen(args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    except OSError as e:
        print "Couldn't start %s, skipping ('%s')" % (name, e)
    else:
        stdout, _ = p.communicate()
        if p.returncode or (output_is_error and stdout.strip()):
            print "%s problems:" % name
            lines = stdout.splitlines()
            if strip_first_line:
                lines = lines[1:]
            for line in lines:
                print '    {}'.format(line)
            success = False
    return success

# MAIN PROGRAM STARTS HERE

if sys.argv[1] == 'check':
    pass
elif sys.argv[1] == 'install':
    for app, hint in (('python', 'https://www.python.org/downloads/'),
                      ('pylint', 'http://www.pylint.org/#install'),
                      ('pep8', 'http://pep8.readthedocs.org/en/latest/'),
                      ('pep257', 'http://pep257.readthedocs.org/en/latest/'),
                      ('yapf', 'https://github.com/google/yapf'), ):
        if not distutils.spawn.find_executable(app):
            print "Couldn't find %s (hint: %s)" % (app, hint)
    sys.exit(0)
else:
    print "Unknown action %s" % sys.argv[1]
    sys.exit(PENDER_ERR)

REAL_FILE = sys.argv[2]
TEMP_FILE = sys.argv[3]
FILE_MIME = sys.argv[4]

# Check the file is Python
if not (REAL_FILE.endswith('.py') or FILE_MIME == 'text/x-python'):
    sys.exit(PENDER_OK)
rc = PENDER_OK

# Check syntax
if USE_PYTHON:
    # XXX: Doesn't handle py2/py3 confusion
    python_args = ('python', '-m', 'py_compile', TEMP_FILE)
    if not check_linter('python', python_args):
        rc = PENDER_VETO

# Check PyLint
if USE_PYLINT:
    pylint_args = ['pylint', '--reports=no',
                   '--msg-template={line:3d}: {msg} ({msg_id})']
    if MAX_LINE_LENGTH:
        pylint_args.append('--max-line-length=%s' % MAX_LINE_LENGTH)
    pylint_args.append('-d=%s' % ','.join(PYLINT_IGNORED_CODES))
    pylint_args.append(TEMP_FILE)
    # Drop the first line, which is like '************* Module pre-commit'
    if not check_linter('pylint', pylint_args, strip_first_line=True):
        rc = PENDER_VETO

# Check pep8
if USE_PEP8:
    pep8_args = ['pep8', '--format=%(row)3d,%(col)3d: %(text)s (%(code)s)']
    if MAX_LINE_LENGTH:
        pep8_args.append('--max-line-length=%s' % MAX_LINE_LENGTH)
    pep8_args.append(TEMP_FILE)
    if not check_linter('pep8', pep8_args):
        rc = PENDER_VETO

# Check pep257
if USE_PEP257:
    pep257_args = ['pep257']
    pep257_args.append('--ignore=%s' % ','.join(PEP257_IGNORED_CODES))
    pep257_args.append(TEMP_FILE)
    if not check_linter('pep257', pep257_args):
        rc = PENDER_VETO

# Check YAPF
if USE_YAPF:
    yapf_args = ('yapf', '-d', '--style=%s' % YAPF_STYLE, TEMP_FILE)
    if not check_linter('yapf', yapf_args, output_is_error=True):
        rc = PENDER_VETO

sys.exit(rc)
