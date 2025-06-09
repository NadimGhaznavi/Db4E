#!/bin/bash

# Script to update the GitHub pages site (e.g. https://xmr.osoyalce.com/) from
# the template GitHub pages site in the db4e project 
# (i.e. https://github.com:NadimGhaznavi/db4e).
#

ENVIRON=$1

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

rsync -avr ${DB4E_DIR}/tmpl/repo/* ${WEB_DIR}
cd $WEB_DIR
git add . -v
git commit -m "Static update"
git push
