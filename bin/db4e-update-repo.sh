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


SRC_DIR=$1
DEST_DIR=$2

# WARNING: Do *NOT* use trailing slashes (/) on the directories
#
#     BAD: db4d-update-repo.sh /home/sally/db4e/tmpl/repo /home/sally/xmr/
#                                                                        ^
#
#    GOOD: db4d-update-repo.sh /home/sally/db4e/tmpl/repo /home/sally/xmr

if [ -z $DEST_DIR ]; then
	echo "ERROR: Usage: $0 /path/to/db4e/tmpl/repo /path/to/local/github/repo"
	exit 1
fi

echo "rsync output:"
echo "-----------------------------------------------------------"
rsync -avr ${SRC_DIR}/* ${DEST_DIR}
echo "-----------------------------------------------------------"
echo -n "Pushing the new files to GitHub: "
cd $DEST_DIR
git add . -v > /dev/null 2>&1
git commit -m "Static update" > /dev/null 2>&1
git push > /dev/null 2>&1
echo "DONE"
