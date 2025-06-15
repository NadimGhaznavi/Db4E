---
title: Utilities
layout: default
---

# db4e.py

This utility monitors the Mining Farm's P2Pool daemon logs, creates records in the backend database and triggers updates to the web front end. See the [db4e.py page](/pages/db4e.py.html) for more information.

---

# db4e-gui.py

The *db4e-gui.py* application provides a console based monitoring solution for my Monero XMR Mining farm.See the [db4e-gui.py page](/pages/db4e-gui.py.html) for more information.

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

---

# db4e-update-repo.sh

The *db4e-update-repo.sh* script ised to update GitHub pages site when there is a new release of *db4e* that includes updates to the static content of the *GitHub Pages website". For example, an update to the contents of the included [Getting Started](/pages/Getting-Started.html) page.

When you run a `git pull` in your local *db4e* folder to get the latest software those static content changes need to be copied into your *GitHub Pages* reposity. The utility
uses rsync to do this.

**WARNING**: Do **NOT** use a trailing slash (/) for the destination directory. It will 
cause bad things to happen with rsync.

This is **wrong**:
```
db4d-update-repo.sh /home/sally/db4e/tmpl/repo /home/sally/xmr/
                                                              ^
```

This is good:
```
db4d-update-repo.sh /home/sally/db4e/tmpl/repo /home/sally/xmr
```

---

# db4e-purge-logs.sh

The *db4e* application sends log messages to a dedicated MongoDB collection (*logging*). The *db4e-purge-logs.sh* deletes old log entries from this collection. The retention time
is defined in the `conf/db4e_prod.yml` file by the *log_retention_days* in the *db* section. 

**PRO TIP:** Run this on a daily basis with a cronjob.