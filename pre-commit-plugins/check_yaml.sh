#!/bin/bash

REAL_FILE=$1
TEMP_FILE=$2
#FILE_MIME=$3
PENDER_OK=0
PENDER_VETO=10

if [[ $REAL_FILE != *.yaml ]] ; then
        exit "$PENDER_OK"
fi

python -c "import yaml; yaml.load(open('$TEMP_FILE'))" 2>&1 | awk '/^yaml/ {p=1} p;'
syntax_rc=${PIPESTATUS[0]}

if [[ $syntax_rc != 0 ]] ; then
    exit $PENDER_VETO
else
    exit $PENDER_OK
fi
