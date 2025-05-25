---
title: Database Backup Utility
---

The `backup-db.sh` script is responsible for backing up the MongoDb database.

* The script is run once a day from a cron job.
* 7 days of backups are maintained.
* The script uses the [gitpush.sh utility](/pages/gitpush.sh.html) to push the backups to Github for off-site storage.

Because the MongoDB backups are in BSON format and are further gzipped, the size is very, very small. The size of a full daily backup of the entire DB is only 216 Kb.

[Back](/)