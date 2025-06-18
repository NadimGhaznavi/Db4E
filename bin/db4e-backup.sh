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

set -euo pipefail

DB_NAME="$1"
COL_NAME="$2"
BACKUP_DIR="$3"
MAX_BACKUPS="${4:-7}"

DEBUG_GIT=false
DEBUG_MONGO=false

usage() {
  echo "Usage: $0 DB_NAME COL_NAME BACKUP_DIR [MAX_BACKUPS]"
  exit 1
}

if [[ -z "${DB_NAME}" || -z "${COL_NAME}" || -z "${BACKUP_DIR}" ]]; then
  usage
fi

mkdir -p "${BACKUP_DIR}"

# Timestamp format: yyyy-mm-dd_hh:mm
TIMESTAMP=$(date '+%Y-%m-%d_%H:%M')
BASENAME="${DB_NAME}_${COL_NAME}_${TIMESTAMP}"
ARCHIVE_PATH="${BACKUP_DIR}/${BASENAME}.archive"

# Create the archive
if [ "$DEBUG_MONGO" = true ]; then
  mongodump --archive="${ARCHIVE_PATH}" --db="${DB_NAME}" --collection="${COL_NAME}"
else
  mongodump --archive="${ARCHIVE_PATH}" --db="${DB_NAME}" --collection="${COL_NAME}" > /dev/null 2>&1
fi

gzip "${ARCHIVE_PATH}"

# Clean up older backups exceeding MAX_BACKUPS
cd "${BACKUP_DIR}"
BACKUP_FILES=( $(ls -1t ${DB_NAME}_${COL_NAME}_*.archive.gz 2>/dev/null) )
TOTAL_FILES=${#BACKUP_FILES[@]}

if (( TOTAL_FILES > MAX_BACKUPS )); then
  for (( i=MAX_BACKUPS; i<TOTAL_FILES; i++ )); do
    rm -f "${BACKUP_FILES[$i]}"
  done
fi

# Git commit
if [ "$DEBUG_GIT" = true ]; then
  git add .
  git commit -m "New backup: ${BASENAME}"
  git push
else
  git add . > /dev/null 2>&1
  git commit -m "New backup: ${BASENAME}" > /dev/null 2>&1 || true
  git push > /dev/null 2>&1 || true
fi

