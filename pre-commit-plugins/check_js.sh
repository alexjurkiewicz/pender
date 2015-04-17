#!/bin/bash

# A Pender plugin to lint JS files. Uses jshint.
# There are no configuration options.

case $1 in
    install)
        if ! which jshint >/dev/null 2>&1 ; then
            echo "jshint not installed (hint: http://jshint.com/install/)"
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
PENDER_OK=0
PENDER_VETO=10

if [[ $REAL_FILE != '*.js' ]] && [[ $REAL_FILE != '*.jsx' ]] ; then
    exit "$PENDER_OK"
fi

if which jshint >/dev/null ; then
    jshint "$TEMP_FILE"
    jshint_rc=$?
else
    echo "jshint not installed, skipping Javascript linting."
    jshint_rc=0
fi

if [[ $jshint_rc != 0 ]] ; then
    exit $PENDER_VETO
else
    exit $PENDER_OK
fi
