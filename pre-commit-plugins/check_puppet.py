#!/usr/bin/env python
"""Pender plugin to check Puppet files using puppet syntax and puppet-lint."""

# CHECK CONFIG
PUPPET_LINT_IGNORE_RULES = []  # list
# END CHECK CONFIG

import sys
import subprocess
import distutils.spawn

PENDER_OK = 0
PENDER_VETO = 10
PENDER_ERR = 1


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


def check_deps():
    """Check dependencies are installed."""
    if not distutils.spawn.find_executable('puppet'):
        print "Couldn't find puppet (hint: " \
            "https://puppetlabs.com/misc/download-options )."
    if not distutils.spawn.find_executable('puppet-lint'):
        print "Couldn't find puppet-lint (hint: gem install puppet-lint)"


if __name__ == '__main__':
    if sys.argv[1] == 'check':
        REAL_FILE = sys.argv[2]
        TEMP_FILE = sys.argv[3]
        # FILE_MIME = sys.argv[4]
        check_puppet()
    elif sys.argv[1] == 'install':
        check_deps()
    else:
        print "Unknown action %s" % sys.argv[1]
        sys.exit(PENDER_ERR)
