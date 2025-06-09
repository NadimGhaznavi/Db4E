---
title: Utilities
layout: default
---

# db4e.py

This utility monitors the Mining Farm's P2Pool daemon logs, creates records in the backend database and triggers updates to the web front end. See the [db4e.py page](/pages/ops/db4e.py.html) for more information.

---

# db4e-gui.py

The *db4e-gui.py* application provides a console based monitoring solution for my Monero XMR Mining farm.See the [db4e-gui.py page](/pages/ops/db4e-gui.py.html) for more information.

---

# db4e-backup.sh

The *backup-db.sh* utility is used to backup the backend MongoDB database. The database contains all of the historical data that the [db4e.py](/pages/ops/db4e.py.html) application collects. See the [backup-db.sh page](/pages/ops/backup-db.sh.html) for more information.

---

# db4e-git.sh

The *db4e-git.sh* utility is responsible for pushing files to GitHub where they are picked up by the JavaScript code and rendered into graphs and bar charts.

---

# db4e-restart.sh

The *db4e-restart.sh* script executed once a day from a cron job. It performs the following sequenced actions:

1. Restart the Monero XMR daemon which is responsible for running the full blockchain node. The node is part of the larger, distributed Monero XMR ecosystem.
2. Restart my Mining Farm's P2Pool daemon.
3. Restart the *db4e* P2Pool log file monitoring daemon.

Additionally, each miner also has a cron job to restart the *xmrig* mining software. Best practice is to restart on a scheduled basis.

# db4e-update-repo.sh

Used to update GitHub pages site when there is a new release of the *db4e*. This updates your GitHub pages repository with content from *tmpl/repo* using *rsync*.
