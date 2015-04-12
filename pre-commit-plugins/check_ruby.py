#!/usr/bin/env python
"""A Pender plugin to check Ruby & ERB files."""

import sys
import subprocess
import distutils.spawn

PENDER_OK = 0
PENDER_VETO = 10
PENDER_ERR = 1


def check_erb():
    """Check ERB file syntax."""
    erb_proc = subprocess.Popen(['erb', '-P', '-x', '-T', '-', TEMP_FILE],
                                stdout=subprocess.PIPE)
    ruby_proc = subprocess.Popen(["ruby", "-c"],
                                 stdin=erb_proc.stdout,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
    erb_proc.stdout.close()  # XXX: is this right??
    output = ruby_proc.communicate()[0].strip()
    if output == 'Syntax OK':
        return PENDER_OK
    else:
        for line in output.splitlines():
            print '    {}'.format(line)
        return PENDER_VETO


def check_ruby():
    """Check Ruby file syntax."""
    try:
        subprocess.check_output(['ruby', '-c', TEMP_FILE],
                                stderr=subprocess.STDOUT)
        return PENDER_OK
    except subprocess.CalledProcessError as err:
        print "Ruby syntax check failed:"
        for line in err.output.splitlines():
            print '    {}'.format(line)
        return PENDER_VETO


if __name__ == '__main__':
    if sys.argv[1] == 'check':
        pass
    elif sys.argv[1] == 'install':
        for app, hint in (('ruby', 'https://www.ruby-lang.org/en/downloads/'),
                          ('erb', 'https://www.ruby-lang.org/en/downloads/'),
                          ):
            if not distutils.spawn.find_executable(app):
                print "Couldn't find %s (hint: %s)" % (app, hint)
        sys.exit(0)
    else:
        print "Unknown action %s" % sys.argv[1]
        sys.exit(PENDER_ERR)

    REAL_FILE = sys.argv[2]
    TEMP_FILE = sys.argv[3]
    FILE_MIME = sys.argv[4]

    # See if we should run
    if not (REAL_FILE.endswith('.rb') or REAL_FILE.endswith('.erb') or
            FILE_MIME == 'text/x-ruby'):
        sys.exit(PENDER_OK)
    if not distutils.spawn.find_executable('ruby'):
        print "ruby not installed, skipping check."
        sys.exit(1)
    if REAL_FILE.endswith('.rb'):
        sys.exit(check_ruby())
    else:  # .erb
        if not distutils.spawn.find_executable('erb'):
            print "erb not installed, skipping check."
            sys.exit(1)
        sys.exit(check_erb())
