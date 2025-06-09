#!/bin/bash

# Script to update the GitHub pages site (e.g. https://xmr.osoyalce.com/) from
# the template GitHub pages site in the db4e project 
# (i.e. https://github.com:NadimGhaznavi/db4e).
#

ENVIRON=$1

DEBUG=False
# DEBUG=True

if [ -z $ENVIRON ]; then
	ENVIRON=prod
fi

if [ "$ENVIRON" == "prod" ]; then
	WEB_DIR=/opt/prod/xmr
	DB4E_DIR=/opt/prod/db4e
elif [ "$ENVIRON" == "qa" ]; then
	WEB_DIR=/opt/qa/xmrqa
	DB4E_DIR=/opt/qa/db4e
else
	echo "ERROR: Usage $0 [prod|qa]"
	exit 1
fi

cd $WEB_DIR

if [ "${DEBUG}" == "False" ]; then
	rsync -avr ${DB4E_DIR}/tmpl/repo/* ${WEB_DIR} > /dev/null 2>&1
	git add . -v > /dev/null 2>&1
	git commit -m "Static update" > /dev/null 2>&1
	git push
else
	rsync -avr ${DB4E_DIR}/tmpl/repo/* ${WEB_DIR}
	git add . -v
	git commit -m "Static update"
	git push
fi