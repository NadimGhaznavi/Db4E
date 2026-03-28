#!/bin/bash 
#

SRC=/opt/dev/Db4E/db4e
DEST=/opt/dev/Db4E/db4e_venv/lib/python3.11/site-packages/db4e

rm -rf $DEST
mkdir $DEST
rsync -avr --delete $SRC/* $DEST
