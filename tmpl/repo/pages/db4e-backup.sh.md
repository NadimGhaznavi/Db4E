---
title: Database Backup Utility
---

The `db4e-backup.sh` script is responsible for backing up the MongoDb database.

* The script is run once a day from a cron job.
* 7 days of backups are maintained.
* The script uses the *db4e-git.sh* utility to push the backups to Github for off-site storage.

Because the MongoDB backups are in BSON format and are further gzipped, the size is very, very small. The size of a full daily backup of the entire DB is only about 50K. 

[Back](/)








