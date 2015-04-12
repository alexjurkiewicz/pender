#!/usr/bin/env python
"""Pender plugin to check Puppet files using puppet syntax and puppet-lint."""

# CHECK CONFIG
PUPPET_LINT_IGNORE_RULES = []  # list
# END CHECK CONFIG

import sys
import subprocess

REAL_FILE = sys.argv[1]
TEMP_FILE = sys.argv[2]
# FILE_MIME = sys.argv[3]
PENDER_OK = 0
PENDER_VETO = 10


def check_puppet():
    """Check Puppet syntax."""
    # See if we should run
    if REAL_FILE[-3:] != '.pp':
        return PENDER_OK

    exit_code = PENDER_OK

    # Syntax
    try:
        syntax_args = ['puppet', 'parser', 'validate', TEMP_FILE]
        subprocess.check_output(syntax_args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        exit_code = PENDER_VETO
        print "Puppet syntax check failed:"
        for line in err.output.splitlines():
            if 'Warning: You cannot collect exported resources without ' \
                    'storeconfigs being set' in line:
                continue
            if 'Warning: You cannot collect without storeconfigs being set' in \
                    line:
                continue
            print '    {}'.format(line)

    # puppet-lint
    try:
        lint_args = ['puppet-lint', '--fail-on-warnings'] + \
            PUPPET_LINT_IGNORE_RULES + [TEMP_FILE]
        subprocess.check_output(lint_args)
    except subprocess.CalledProcessError as err:
        exit_code = PENDER_VETO
        print "puppet-lint failed:"
        for line in err.output.splitlines():
            print '    {}'.format(line)

    sys.exit(exit_code)


if __name__ == '__main__':
    check_puppet()
