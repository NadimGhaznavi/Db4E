#!/bin/bash

# This script is used to deploy new db4e releases into the db4e 
# website GitHub repository. 
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


ENVIRON=$1
WEB_DIR=$2

if [ -z $WEB_DIR ]; then
	echo "ERROR: Usage: $0 [qa|prod] [/path/to/github/pages/repo]"
	exit 1
fi

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

echo "rsync output"
echo "-----------------------------------------------------------"
rsync -avr ${DB4E_DIR}/tmpl/repo/* ${WEB_DIR}
echo "-----------------------------------------------------------"
echo -n "Pushing the new files to GitHub: "
git add . -v > /dev/null 2>&1
git commit -m "Static update" > /dev/null 2>&1
git push > /dev/null 2>&1
echo "DONE
