#!/bin/bash

# A Pender plugin to lint shell scripts. Uses bash & shellcheck.
# Configuration:
#   skip_shellcheck: if set to anything, don't try to use shellcheck.

# Exit codes
PENDER_OK=0
PENDER_VETO=10

# See if we should use shellcheck
use_shellcheck() {
    if [[ -n $PENDER_skip_shellcheck ]] ; then
        return 1
    fi
    if ! which shellcheck >/dev/null 2>&1 ; then
        echo "shellcheck not installed (hint: http://www.shellcheck.net/about.html)"
        return 1
    fi
}

main() {
    # Check the file is a shell script
    if ! ( [[ $REAL_FILE == *.sh ]] || [[ $FILE_MIME == 'text/x-shellscript' ]] ) ; then
        exit "$PENDER_OK"
    fi

    # Check syntax with bash -n
    bash -n "$TEMP_FILE" 2>&1
    bash_rc=$?

    # Lint file with shellcheck
    if use_shellcheck ; then
        shellcheck "$TEMP_FILE"
        shellcheck_rc=$?
    else
        shellcheck_rc=0
    fi

    # Veto the commit if either check failed
    if [[ $bash_rc != 0 ]] || [[ $shellcheck_rc != 0 ]] ; then
        exit $PENDER_VETO
    else
        exit $PENDER_OK
    fi
}

# Program starts here
case $1 in
    install)
        use_shellcheck
        exit 0
        ;;
    check)
        REAL_FILE=$2
        TEMP_FILE=$3
        FILE_MIME=$4
        main
        ;;
    *)
        echo "Unknown action $1"
        ;;
esac
