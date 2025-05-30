---
title: The Database 4 Everything - db4e
---
# Table of Contents

* [Introduction and Scope](#introduction-and-scope)
* [Realtime Data on the Web](#realtime-data-on-the-web)
* [Systems Architecture](#systems-architecture)
* [Command Line Utilities](#command-line-utilities)
* [Backend Components](#backend-components)
* [Systems Configuration](#systems-configuration)
* [Software Build Documentation](#software-build-documentation)
* [Hardware](#hardware)
* [Links](#links)

---

# Introduction and Scope

This is the home of the **db4e**, **Database 4 Everything**  project. The **db4e** application is used to provide a [console based dashboard](/pages/ops/db4e-gui.py.html) and near real-time [visualizations](/pages/web/index.html) to monitor a local Monero XMR Mining farm that uses a local P2Pool node.

---

# Realtime Data on the Web

The *db4e* application is event driven. When a new event is received it generates new data which is displayed by the [db4e console GUI](/pages/ops/db4e-gui.py.html) and [this site](/pages/web/index.html).

The following events are captured:

* [XMR payments](/pages/web/P2Pool-Payouts-Short.html) made to the mining farm
* [Shares found](/pages/web/Shares-Found-Short.html) by my mining farm
* [Blocks found](/pages/web/Blocks-Found-Short.html) on the Monero XMR mini sidechain
* [Hashrate of my pool](/pages/web/Pool-Hashrate-Short.html), the [mini sidechain](/pages/web/Sidechain-Hashrate-Short.html) and the [mainchain](/pages/web/Mainchain-Hashrate-Short.html) over time

---

# Systems Architecture

The *db4d* application is made up of a number of components:

* The core *db4e* Python code
* A running 

# Command Line Utilities

## db4e.py

This utility monitors the Mining Farm's P2Pool daemon logs, creates records in the backend database and triggers updates to the web front end. See the [db4e.py page](/pages/ops/db4e.py.html) for more information.

## db4e-gui.py

The `db4e-gui.py` application provides a console based monitoring solution for my Monero XMR Mining farm.See the [db4e-gui.py page](/pages/ops/db4e-gui.py.html) for more information.

## backup-db.sh

The `backup-db.sh` utility is used to backup the backend MongoDB database. The database contains all of the historical data that the [db4e.py](/pages/ops/db4e.py.html) application collects. See the [backup-db.sh page](/pages/ops/backup-db.sh.html) for more information.

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

---

# Backend Components

I designed the application to be modular and have a clear data abstraction layer. While the *Database 4 Everything* application is currently only being used to house data on my Monero XMR Mining farm, I designed it to be easily extended to house other data (e.g. system update, disk usage, CPU utilization and memory metrics).

## Infrastructure Modules

Module      | Description
------------|--------------------
Db4eDb      | This module is responsible for all MongoDb operations.
Db4eLog     | This module is responsible for managing logging of the application.
Db4eStartup | This module is responsible for loading *db4e* settings from an INI file.

## Mining Modules

Module               | Description
---------------------|--------------------------------------
MiningDb             | Accepts mining specific DB commands and then uses the Db4eDb module to execute them.
P2Pool               | Monitors the P2Pool daemon log file and creates corresponding events in MongoDb using the MiningDb module.

The modules below are called by the P2Pool module when the corresponding event is detected. These modules extract all historical data for the event, aggregate it into daily totals, writes that data to a CSV file and pushes the file to GitHub where it is rendered by Javascript Apexcharts code.

Module               | Description
---------------------|--------------------------------------
BlocksFoundCsv       | Monero mini sidechain block found events.
SharesFoundCsv       | Share found events in my mining farm.
SharesFoundByHostCsv | Share found events, by host, in my mining farm.
P2PoolPaymentCsv     | XMR payments made to my mining farm.

---

# Systems Configuration

* [Configuring the Monero Daemon as a Service](/pages/ops/Configuring-the-Monero-Daemon-as-a-Service.html)
* [Configuring the P2Pool Daemon as a Service](/pages/ops/Configuring-the-P2Pool-Daemon-as-a-Service.html)
* [Secondary Monero Daemon Configuration](/pages/ops/Secondary-Monero-Daemon-Configuration.html)
* [Port Forwarding with upnpc](/pages/ops/Port-Forwarding-With-upnpc.html)

---

# Software Build Documentation

* [Building P2Pool from Source](/pages/ops/Building-P2Pool-from-Source.html)
* [Building Monerod from Source](/pages/ops/Building-Monerod-from-Source.html)

---

# Hardware

* [Miner CPU and Memory Specs](/pages/ops/Miner-Specs.html)

---

# Links

* The *db4e* source code for this site [GitHub](https://github.com/NadimGhaznavi/db4e).
