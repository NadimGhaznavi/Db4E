#!/bin/bash

# Script to update the GitHub pages site (e.g. https://xmr.osoyalce.com/) from
# the template GitHub pages site in the db4e project 
# (i.e. https://github.com:NadimGhaznavi/db4e).
#

ENVIRON=$1
WEB_DIR=$2

if [ -z $WEB_DIR ]; then
	echo "ERROR: Usage: $0 [qa|prod] [/path/to/github/pages/repo]"
	exit 1
fi

DEBUG=False
# DEBUG=True

if [ "$ENVIRON" == "prod" ]; then
	WEB_DIR=/opt/prod/xmr
	DB4E_DIR=/opt/prod/db4e
elif [ "$ENVIRON" == "qa" ]; then
	WEB_DIR=/opt/qa/xmrqa
	DB4E_DIR=/opt/qa/db4e
else
	echo "ERROR: Usage $0 [prod|qa] [/path/to/github/pages/repo]"
	exit 1
fi

cd $WEB_DIR

if [ "${DEBUG}" == "False" ]; then
	rsync -avr ${DB4E_DIR}/tmpl/repo/* ${WEB_DIR} > /dev/null 2>&1
	git add . -v > /dev/null 2>&1
	git commit -m "Static update" > /dev/null 2>&1
	git push > /dev/null 2>&1
else
	rsync -avr ${DB4E_DIR}/tmpl/repo/* ${WEB_DIR}
	git add . -v
	git commit -m "Static update"
	git push
fi
