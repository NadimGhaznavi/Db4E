#!/bin/bash -x

ENV=$1

if [ -z ${ENV} ]; then
  echo "Usage: $0 [dev|qa|prod]"
  exit 1
fi

if [ "${ENV}" == "prod" ]; then
  DB_NAME=db4e
  BACKUP_DIR=/opt/prod/db4e/db
elif [ "${ENV}" == "qa" ]; then
  DB_NAME=db4e_qa
  BACKUP_DIR=/opt/prod/db4e/db
elif [ "${ENV}" == "dev" ]; then
  DB_NAME=db4e_dev
  BACKUP_DIR=/home/sally/xmr/data
else
  echo "Usage: $0 [dev|qa|prod]"
  exit 1
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
git add dump/${DB_NAME}/mining.bson
git add dump/${DB_NAME}/mining.metadata.json
git add dump/${DB_NAME}/prelude.json
git commit -m "New backup"
git push

