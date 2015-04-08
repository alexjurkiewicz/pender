#!/usr/bin/env python

'''
This is a Pender plugin to check Python files using python syntax, pylint and flake8 (pyflakes & pep8)
'''

# CHECK CONFIG
MAX_LINE_LEN = 120  # flake8 default is 79
PYLINT_IGNORE_CHECKS = ['W0511']  # list
# END CHECK CONFIG

import sys
import subprocess

REAL_FILE = sys.argv[1]
TEMP_FILE = sys.argv[2]
FILE_MIME = sys.argv[3]
PENDER_OK = 0
PENDER_VETO = 10


def check_syntax(temp_file):
    '''
    Check python syntax of the target file
    '''
    try:
        subprocess.check_output(['python', '-m', 'py_compile', temp_file])
    except subprocess.CalledProcessError as err:
        print "Python syntax check failed:"
        for line in err.output.splitlines():
            print '    {}'.format(line)
        return PENDER_VETO
    return PENDER_OK


def check_pylint(temp_file):
    '''
    PyLint
    Exclude:
      - C0301: line too long (reported better by pyflake E501)
      - C0330: Wrong hanging indentation. (reported better by pyflake E126)
    '''
    try:
        pylint_cmdline = ['pylint',
                          '--disable={}'.format(','.join(PYLINT_IGNORE_CHECKS + ['C0301', 'C0330'])),
                          '--rcfile=/dev/null',
                          '--reports=n',
                          '--msg-template={line:3d}: {msg} ({msg_id})',
                          temp_file]
        subprocess.check_output(pylint_cmdline)
    except subprocess.CalledProcessError as err:
        print "Pylint check failed:"
        for line in err.output.splitlines():
            print '    {}'.format(line)
        return PENDER_VETO
    return PENDER_OK


def check_pyflake(temp_file):
    '''
    PyFlake
    Exclude:
      - E225 missing whitespace around operator (pylint C0326)
      - F821 undefined name (pylint E0602)
      - F841 local variable '...' is assigned to but never used (pylint W0612)
      - E701 multiple statements on one line (colon) (pylint C0321)
    '''
    try:
        subprocess.check_output(['flake8',
                                 '--max-line-length={}'.format(MAX_LINE_LEN),
                                 '--ignore=E225,F821,E701',
                                 '--format=%(row)3d: %(text)s (%(code)s)',
                                 temp_file])
    except subprocess.CalledProcessError as err:
        print "flake8 check failed:"
        for line in err.output.splitlines():
            print '    {}'.format(line)
        return PENDER_VETO
    return PENDER_OK


def check_file():
    '''
    Run all checks on file
    '''
    exit_code = PENDER_OK
    exit_code = max(exit_code, check_syntax(TEMP_FILE))
    exit_code = max(exit_code, check_pylint(TEMP_FILE))
    exit_code = max(exit_code, check_pyflake(TEMP_FILE))
    sys.exit(exit_code)

if __name__ == '__main__':
    if not (REAL_FILE.endswith('.py') or FILE_MIME == 'text/x-python'):
        sys.exit(PENDER_OK)
    check_file()
