---
title: The Database 4 Everything - db4e
---
# Table of Contents

* [Introduction and Scope](#introduction-and-scope)
* [Command Line Utilities](#command-line-utilities)
  * [db4e.py](#db4e.py)
* [Links](#links)

# Introduction and Scope

This site documents my **db4e** project. The db4e application is used to provide a console based dashbaord and near real-time visualizations into my [Monero XMR cryptocurrency mining farm](https://xmr.osoyzlce.com/). 

# Command Line Utilities

## db4e.py

This utility monitors the Mining Farm's P2Pool daemon logs, creates records in the backend database and triggers updates to the web front end. See the [db4e.py page](/pages/db4e.py.html) for more information.


db4e-gui.py                | A console application to monitor the health of the mining farm in real-time.
backup-db.sh               | Utility to backup the backend MongoDB database.
gitpush.sh                 | Utility to push files up to Github.
restart_mining_services.sh | Utility to restart all of the Mining Farm's services

# Links

* The *db4e* code on [GitHub](https://github.com/NadimGhaznavi/db4e).

