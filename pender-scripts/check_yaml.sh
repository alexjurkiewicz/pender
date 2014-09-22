#!/bin/bash

REAL_FILE=$1
#TEMP_FILE=$2
#FILE_MIME=$3

if [[ $REAL_FILE != '*.yaml' ]] ; then
        exit 0
fi

python -c "import yaml; yaml.load(open('$testfile'))"

exit 0
