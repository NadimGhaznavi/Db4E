#!/bin/bash

DB_NAME=$1
BACKUP_DIR=$2

if [ ! -d ${BACKUP_DIR} ]; then
  mkdir -p ${BACKUP_DIR}
fi

ARCHIVE=${BACKUP_DIR}/${DB_NAME}

mongodump --archive="${ARCHIVE}.0" --db=${DBNAME}

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
git add .
git commit -m "New backup"
git push

