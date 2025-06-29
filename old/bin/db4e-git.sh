#!/bin/bash
#
# bin/db4e-git.sh
#
# A simple wrapper for git that enables the *db4e* application to run
# git add, commit and push commands.
#
#####################################################################


#####################################################################
#
#  This file is part of *db4e*, the *Database 4 Everything* project
#  <https://github.com/NadimGhaznavi/db4e>, developed independently
#  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
#  <https://github.com/NadimGhaznavi/db4e>.
# 
#  This program is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as 
#  published by the Free Software Foundation, version 3.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy (LICENSE.txt) of the GNU General 
#  Public License along with this program. If not, see 
#  <http://www.gnu.org/licenses/>.
#
#####################################################################


REPO_DIR=$1
OP=$2

#DEBUG=True
DEBUG=False

if [ $DEBUG == "True" ]; then
    echo "db4e-git.sh"
    echo "- Repo is : $REPO_DIR"
    echo "- Op is   : $OP"
fi

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
    if [ $DEBUG == "True" ]; then
        echo "- File is : $FILE"
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
    if [ $DEBUG == "True" ]; then
        echo "- Log msg : $MSG"
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


