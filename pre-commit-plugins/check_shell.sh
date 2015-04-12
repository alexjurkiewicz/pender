#!/bin/bash

case $1 in
    install)
        if ! which shellcheck >/dev/null 2>&1 ; then
            echo "shellcheck not installed (hint: http://www.shellcheck.net/about.html)"
            exit 0
        fi
        ;;
    check)
        shift
        ;;
    *)
        echo "Unknown action $1"
        ;;
esac

REAL_FILE=$1
TEMP_FILE=$2
FILE_MIME=$3
PENDER_OK=0
PENDER_VETO=10

if [[ $REAL_FILE != '*.sh' ]] && [[ $FILE_MIME != 'text/x-shellscript' ]] ; then
    exit "$PENDER_OK"
fi

bash -n "$TEMP_FILE" 2>&1
bash_rc=$?

if which shellcheck >/dev/null ; then
    shellcheck "$TEMP_FILE"
    shellcheck_rc=$?
else
    echo "shellcheck not installed, skipping shell script linting."
    shellcheck_rc=0
fi

if [[ $bash_rc != 0 ]] || [[ $shellcheck_rc != 0 ]] ; then
    exit $PENDER_VETO
else
    exit $PENDER_OK
fi
