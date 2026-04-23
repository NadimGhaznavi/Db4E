#!/bin/bash 
#

SRC=/opt/qa/db4e/db4e/
DEST=/home/dan/db4e_venv/lib/python3.11/site-packages/db4e/

mkdir -p $DEST
rsync -avr --delete "$SRC" "$DEST" | grep -v __pycache__
