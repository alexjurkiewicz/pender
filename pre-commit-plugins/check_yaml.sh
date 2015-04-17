#!/bin/bash

# A Pender plugin to check YAML files. Uses python-yaml.
# There are no configuration options.

case $1 in
    install)
        if ! python -c 'import yaml' 2>/dev/null ; then
            echo "Python-YAML is not installed (hint: pip install PyYAML)"
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
#FILE_MIME=$3
PENDER_OK=0
PENDER_VETO=10

if [[ $REAL_FILE != *.yaml ]] ; then
        exit "$PENDER_OK"
fi

if ! python -c 'import yaml' 2>/dev/null ; then
    echo "Python-YAML is not installed (hint: pip install PyYAML)"
    exit $PENDER_OK
fi

python -c "import yaml; yaml.load(open('$TEMP_FILE'))" 2>&1 | awk '/^yaml/ {p=1} p;'
syntax_rc=${PIPESTATUS[0]}

if [[ $syntax_rc != 0 ]] ; then
    exit $PENDER_VETO
else
    exit $PENDER_OK
fi
