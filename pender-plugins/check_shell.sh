#!/bin/bash

REAL_FILE=$1
TEMP_FILE=$2
FILE_MIME=$3
PENDER_OK=0
PENDER_VETO=10

if [[ $FILE_MIME != 'text/x-shellscript' ]] && [[ $REAL_FILE != '*.sh' ]] ; then
    exit "$PENDER_OK"
fi

bash -n "$TEMP_FILE" 2>&1
bash_rc=$?

shellcheck "$TEMP_FILE"
shellcheck_rc=$?

if [[ $bash_rc != 0 ]] || [[ $shellcheck_rc != 0 ]] ; then
    exit $PENDER_VETO
else
    exit $PENDER_OK
fi
