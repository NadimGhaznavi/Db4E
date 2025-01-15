#!/bin/bash 

# Script to push a file to GitHub

# The directory where the file to be pushed lives
SRCDIR=$1
FILENAME=$2
COMMENT=$3
DEBUG=$4

cd ${SRCDIR}

if [ "null$DEBUG" != "null" ]; then
  echo "gitpush.sh"
  echo "  SRCDIR: $SRCDIR"
  echo "  FILENAME: $FILENAME"
  echo "  COMMENT: $COMMENT"
  echo "  DEBUG: $DEBUG"
  git add ${FILENAME}
  git commit -m "${COMMENT}"
  git push -v 
  echo
else
  git add ${FILENAME} > /dev/null 2>&1
  git commit -m "${COMMENT}" > /dev/null 2>&1
  git push > /dev/null 2>&1
fi



