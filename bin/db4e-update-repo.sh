#!/bin/bash

# Script to update the GitHub pages site (e.g. https://xmr.osoyalce.com/) from
# the template GitHub pages site in the db4e project 
# (i.e. https://github.com:NadimGhaznavi/db4e).

WEB_DIR=/opt/qa/xmrqa
DB4E_DIR=/opt/qa/db4e

rsync -avr ${DB4E_DIR}/tmpl/repo/* ${WEB_DIR}