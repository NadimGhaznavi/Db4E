#!/bin/bash
#

echo "Dropping the db4e_qa database...."
mongosh --eval "use db4e_qa; db.dropDatabase();"

