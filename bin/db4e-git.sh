#!/bin/bash

# A simple wrapper for git.

# This script assumes you have a valid git repository setup and are using credentials
# that allow git's 'add', 'commit' and 'push' commands.

REPO_DIR=$1
OP=$2

if [ -z $OP ];then
    echo "Usage: $0 /path/to/repo [add|commit|push]"
    exit 1
fi

if [ "$OP" == "add" ]; then
    FILE=$3
    if [ -z $FILE ]; then
        echo "Usage: $0 add /path/to/repo/file"
        exit 1
    fi
    cd $REPO_DIR
    git add $FILE
fi
