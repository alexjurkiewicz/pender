#!/bin/bash

REAL_FILE=$1
TEMP_FILE=$2
FILE_MIME=$3

if [[ $FILE_MIME != 'text/x-shellscript' ]] && [[ $REAL_FILE != '*.sh' ]] ; then
    exit 0
fi

bash -n "$TEMP_FILE" 2>&1

shellcheck "$TEMP_FILE"

exit 0
