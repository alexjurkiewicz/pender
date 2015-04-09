#!/usr/bin/env python

"""
A Pender plugin to check Python files.
"""

import os
import sys
import subprocess
import distutils.spawn

REAL_FILE = sys.argv[1]
TEMP_FILE = sys.argv[2]
FILE_MIME = sys.argv[3]
PENDER_OK = 0
PENDER_VETO = 10
DEBUG = True if 'PENDER_DEBUG' in os.environ else False

available_linters = ('pylint', 'pep8', 'pep257', 'pyfake')
# Check dependencies are installed
linters = []
for linter in available_linters:
    if distutils.spawn.find_executable(linter):
        linters.append(linter)
    else:
        print "Mising Python linter %s, you should install this!" % linter
PYLAMA_ARGS = ('pylama', '-l', ','.join(linters), '-i', 'C0111,C0303', TEMP_FILE)

rc = PENDER_OK
# Check the file is Python
if not (REAL_FILE.endswith('.py') or FILE_MIME == 'text/x-python'):
    sys.exit(PENDER_OK)

# Check syntax
try:
    subprocess.check_output(['python', '-m', 'py_compile', TEMP_FILE])
except subprocess.CalledProcessError as err:
    print "Python syntax check failed:"
    for line in err.output.splitlines():
        print '    {}'.format(line)
    rc = PENDER_VETO

# Check PyLama
try:
    subprocess.check_output(PYLAMA_ARGS)
except subprocess.CalledProcessError as err:
    print "pylama check failed:"
    for line in err.output.splitlines():
        # pylama prints the full file path before each error
        # we want to hide the temporary file path
        try:
            line = line[line.index(REAL_FILE):]
        except ValueError:
            pass
        print '    {}'.format(line)
    sys.exit(PENDER_VETO)

sys.exit(rc)

