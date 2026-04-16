#!/bin/bash 
#

SRC=/opt/dev/Db4E/db4e/
DEST=/opt/dev/Db4E/db4e_venv/lib/python3.11/site-packages/db4e/

mkdir -p $DEST
rsync -avr --delete "$SRC" "$DEST" | grep -v __pycache__
