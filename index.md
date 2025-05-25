---
title: The Database 4 Everything - db4e
---
# Table of Contents

* [Introduction and Scope](#introduction-and-scope)
* [Command Line Utilities](#command-line-utilities)
  * [db4e.py](#db4e.py)
  * [db4e-gui.py](#db4e-gui.py)
  * [backup-db.sh](#backup-db.sh)
  * [gitpush.sh](#gitpush.sh)
  * [restart_mining_services.sh](#restart-mining-services.sh)
* [Historical Data on the Web](#historical-data-on-the-web)
* [Links](#links)

# Introduction and Scope

This site documents my **db4e** project. The db4e application is used to provide a console based dashbaord and near real-time visualizations into my [Monero XMR cryptocurrency mining farm](https://xmr.osoyzlce.com/). 

# Command Line Utilities

## db4e.py

This utility monitors the Mining Farm's P2Pool daemon logs, creates records in the backend database and triggers updates to the web front end. See the [db4e.py page](/pages/db4e.py.html) for more information.

## db4e-gui.py

The `db4e-gui.py` application provides a console based monitoring solution for my Monero XMR Mining farm.See the [db4e-gui.py page](/pages/db4e-gui.py.html) for more information.

## backup-db.sh

The `backup-db.sh` utility is used to backup the backend MongoDB database. The database contains all of the historical data that the [db4e.py](/pages/db4e.py.html) application collects. See the [backup-db.sh page](/pages/backup-db.sh.html) for more information.

## gitpush.sh

the `gitpush.sh` utility accepts the following arguments:

* Source directory.
* Filename.
* Comment.

It uses these args to execute a `git push` command to push files up to Github.

## restart_mining_services.sh

The `restart_mining_services.sh` script executed once a day from a cron job. It performs the following sequenced actions:

1. Restart the Monero XMR daemon which is responsible for running the full blockchain node. The node is part of the larger, distributed Monero XMR ecosystem.
2. Restart my Mining Farm's P2Pool daemon.
3. Restart the *db4e* P2Pool log file monitoring daemon.

Additionally, each miner also has a cron job to restart the `xmrig` mining software.

Basically, I restart all of my Mining farm's services on a daily basis.

# Historical Data on the Web

When the `db4e` P2Pool daemon log file monitoring daemon watches for events and creates MongoDb records for them. When one of the following events is found:

* XMR payment made to my mining farm
* Share found by my mining farm
* Block found on the Monero XMR mini sidechain

The the application aggregates the daily totals for those events, generates a CSV File and pushes the file to GitHub where it is rendered using some Javascript code based around ApexCharts.

  * [P2Pool Payouts Visualization](https://xmr.osoyalce.com/pages/P2Pool-Payouts.html)
  * [Blocks Found Visualization](https://xmr.osoyalce.com/pages/Blocks-Found.html)
  * [Shares Found Visualization](https://xmr.osoyalce.com/pages/Shares-Found.html)

# Links

* The *db4e* code on [GitHub](https://github.com/NadimGhaznavi/db4e).

