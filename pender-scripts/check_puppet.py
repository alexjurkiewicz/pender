#!/usr/bin/env python

'''
This is a Pender plugin to check Puppet files using puppet syntax and puppet-lint
'''

# CHECK CONFIG
PUPPET_LINT_IGNORE_RULES = []  # list
# END CHECK CONFIG

import sys
import subprocess

REAL_FILE = sys.argv[1]
TEMP_FILE = sys.argv[2]
# FILE_MIME = sys.argv[3]

# See if we should run
if REAL_FILE[-3:] != '.pp':
    sys.exit(0)

# Syntax
try:
    subprocess.check_output(['puppet', 'parser', 'validate', TEMP_FILE])
except subprocess.CalledProcessError as err:
    print "Puppet syntax check failed:"
    print err.output

# puppet-lint
try:
    subprocess.check_output(['puppet-lint', '--fail-on-warnings'] + PUPPET_LINT_IGNORE_RULES + [TEMP_FILE])
except subprocess.CalledProcessError as err:
    print "puppet-lint failed:"
    print err.output

sys.exit(0)
