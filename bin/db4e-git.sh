#!/bin/bash

# A simple wrapper for git.

# This script assumes you have a valid git repository setup and are using credentials
# that allow git's 'add', 'commit' and 'push' commands.

REPO_DIR=$1
OP=$2

DEBUG=True
#DEBUG=False

echo "Repo is ($REPO_DIR)"
echo "Op is ($OP)"

if [ -z $OP ];then
    echo "Usage: $0 /path/to/repo [add|commit|push]"
    exit 1
fi

if [ "$OP" == "add" ]; then
    FILE=$3
    if [ -z $FILE ]; then
        echo "Usage: $0 /path/to/repo add /path/to/repo/file"
        exit 1
    fi
    cd $REPO_DIR
    if [ $DEBUG == "True" ]; then
        git add $FILE
    else
        git add $FILE > /dev/null 2>&1
    fi

elif [ "$OP" == "commit" ]; then
    MSG=$3
    if [ -z "$MSG" ]; then
        echo "Usage: $0 commit \"Log message\""
        exit 1
    fi
    cd $REPO_DIR
    if [ $DEBUG == "True" ]; then 
        git commit -m "$MSG"
    else
        git commit -m "$MSG" > /dev/null 2>&1
    fi

elif [ "$OP" == "push" ]; then
    cd $REPO_DIR
    if [ $DEBUG == "True" ]; then
        git push
    else
        git push > /dev/null 2>&1
    fi
fi


