#!/bin/bash
#
# bin/db4e-backup.sh
#
# Script to run the db4e MongoDB backups. This script backs up the
# 'db4e' MongoDB collection that houses the mining data and the 
# 'logging' collection containing logs for db4e.
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

DB_NAME=$1
COL_NAME=$2
BACKUP_DIR=$3

DEBUG_GIT=False
# DEBUG_GIT=True
DEBUG_MONGO=False
# DEBUG_MONGO=True

if [ -z $BACKUP_DIR ]; then
  echo "ERROR: Usage $0 DB_NAME COL_NAME BACKUP_DIR"
  exit 1
fi

if [ ! -d ${BACKUP_DIR} ]; then
  mkdir -p ${BACKUP_DIR}
fi

ARCHIVE="${BACKUP_DIR}/${DB_NAME}_${COL_NAME}"

if [ "${DEBUG_MONGO}" == "True" ]; then
  mongodump --archive="${ARCHIVE}.0" --db=${DB_NAME} --collection=${COL_NAME}
else
  mongodump --archive="${ARCHIVE}.0" --db=${DB_NAME} --collection=${COL_NAME} > /dev/null 2>&1
fi 

gzip ${ARCHIVE}.0

if [ -f ${ARCHIVE}.7.gz ]; then
  rm ${ARCHIVE}.7.gz
fi

for COUNT in 6 5 4 3 2 1 0; do
  if [ -f ${ARCHIVE}.${COUNT}.gz ]; then
    mv ${ARCHIVE}.${COUNT}.gz ${ARCHIVE}.$((COUNT+1)).gz
  fi
done

cd ${BACKUP_DIR}
if [ "{$DEBUG_GIT}" == "True" ]; then
  git add .
  git commit -m "New backup (${ARCHIVE})"
  git push
else
  git add . > /dev/null 2>&1
  git commit -m "New backup (${ARCHIVE})" > /dev/null 2>&1
  git push > /dev/null 2>&1
fi
