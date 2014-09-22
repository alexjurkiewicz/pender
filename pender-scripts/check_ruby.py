#!/usr/bin/env python

'''
This is a Pender plugin to check Ruby & ERB files.
'''

import sys
import subprocess

REAL_FILE = sys.argv[1]
TEMP_FILE = sys.argv[2]
FILE_MIME = sys.argv[3]


def check_erb():
    '''
    Check ERB file syntax
    '''
    erb_proc = subprocess.Popen(
        ['erb', '-P', '-x', '-T', '-', TEMP_FILE],
        stdout=subprocess.PIPE)
    ruby_proc = subprocess.Popen(
        ["ruby", "-c"],
        stdin=erb_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    erb_proc.stdout.close()
    print ruby_proc.communicate()[0]


def check_ruby():
    '''
    Check Ruby file syntax
    '''
    try:
        subprocess.check_output(['ruby', '-c', TEMP_FILE], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print "Ruby syntax check failed:"
        print err.output


if __name__ == '__main__':
    # See if we should run
    if not (REAL_FILE.endswith('.rb') or REAL_FILE.endswith('.erb') or FILE_MIME == 'text/x-ruby'):
        sys.exit(0)

    if REAL_FILE.endswith('.erb'):
        check_erb()
    else:  # It's pure Ruby
        check_ruby()
