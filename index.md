---
title: The Database 4 Everything
---
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
<script src="/assets/js/SharesFoundByHostShort.js"></script>


<div id="wrapper">
  <div id="areaChart">
  </div>
  <div id="barChart">
  </div>
 </div>

This is the home of the **db4e**, the **Database 4 Everything**  project. The **db4e** application is used to provide a [console based dashboard](/pages/ops/db4e-gui.py.html) and [realtime web based visualizations](/pages/web/index.html) to monitor a local Monero XMR Mining farm that uses a local P2Pool node.
The stacked barchart above is a real-time visualization of the shares found on the Monero sidechain by the miners in the local P2Pool.

---

# Table of Contents

* [Realtime Data on the Web](#realtime-data-on-the-web)
* [Technology Stack](#technology-stack)
* [Codebase Architecture](#codebase-architecture)
* [Systems Configuration](#systems-configuration)
* [Software Build Documentation](#software-build-documentation)
* [Hardware](#hardware)
* [Links](#links)

---

# Realtime Data on the Web

The *db4e* application is event driven. When a new event is received it generates new data which is displayed by the [db4e console](/pages/ops/db4e-gui.py.html) and/or the [db4e web interface](/pages/web/index.html).

The following events are captured:

* [Daily](/pages/web/P2Pool-Payouts-Daily-Short.html) and [cumulative](/pages/web/P2Pool-Payouts-Short.html) XMR payments made to the mining farm
* [Shares found](/pages/web/Shares-Found-Short.html) by the mining farm
* [Blocks found](/pages/web/Blocks-Found-Short.html) on the Monero XMR mini sidechain
* [Hashrates of my pool](/pages/web/Pool-Hashrate-Short.html), the current [sidechain](/pages/web/Sidechain-Hashrate-Short.html) and the [mainchain](/pages/web/Mainchain-Hashrate-Short.html) over time

---

# Technology Stack

The *db4e* application is currently running on [Debian Linux](https://www.debian.org/) and is made up of a number of components:

* The [core db4e code](https://github.com/NadimGhaznavi/db4e)
* A [P2Pool daemon](/pages/ops/Building-P2Pool-from-Source.html)
* A [GitHub](https://github.com/) account and repository
* A [MongoDB server](/pages/ops/Installing-MongoDB.html)

At it's core, *db4e* monitors the P2Pool server for events. Scheduled commands are also sent to the running P2Pool daemon to trigger log output. Events are stored in MongoDB. Some events also trigger the creation of a CSV file which is published to a GitHub hosted website (this site). Javascript code is used to render the CSV data into nice, human-friendly graphs and bar charts.

See the [Pre-Requisites page](/pages/ops/Pre-Requisites.md)

---

# Codebase Architecture

The application is designed to be modular and have a clear data abstraction layer. Mining database operations go though a *mining
database class* which sends those to a *db4e mining class* which interacts with MongoDB.

For example, mining data exports to CSV are performed by connecting to the *MiningDb* class which connects to the *Db4eDb* class which connects to MongoDb and fetches the data.

---

## Command Line Utilities

---

### db4e.py

This utility monitors the Mining Farm's P2Pool daemon logs, creates records in the backend database and triggers updates to the web front end. See the [db4e.py page](/pages/ops/db4e.py.html) for more information.

---

### db4e-gui.py

The `db4e-gui.py` application provides a console based monitoring solution for my Monero XMR Mining farm.See the [db4e-gui.py page](/pages/ops/db4e-gui.py.html) for more information.

---

### backup-db.sh

The `backup-db.sh` utility is used to backup the backend MongoDB database. The database contains all of the historical data that the [db4e.py](/pages/ops/db4e.py.html) application collects. See the [backup-db.sh page](/pages/ops/backup-db.sh.html) for more information.

---

### gitpush.sh

the `gitpush.sh` utility is responsible for pushing files to GitHub where they are picked up by the JavaScript code and rendered into graphs and bar charts.

---

### restart_mining_services.sh

The `restart_mining_services.sh` script executed once a day from a cron job. It performs the following sequenced actions:

1. Restart the Monero XMR daemon which is responsible for running the full blockchain node. The node is part of the larger, distributed Monero XMR ecosystem.
2. Restart my Mining Farm's P2Pool daemon.
3. Restart the *db4e* P2Pool log file monitoring daemon.

Additionally, each miner also has a cron job to restart the `xmrig` mining software.

Basically, I restart all of my Mining farm's services on a daily basis.

---

## Infrastructure Modules

Module      | Description
------------|--------------------
Db4eConfig  | This module is responsible for loading *db4e* application settings from an YAML file.
Db4eDb      | This module is responsible for all MongoDb operations.
Db4eGit     | This module is responsible for pushing files up to GitHub.
Db4eLog     | This module is responsible for managing logging of the application.

---

## Mining Modules

Module               | Description
---------------------|--------------------------------------
MiningDb             | Accepts mining specific DB commands and then uses the Db4eDb module to execute them.
P2Pool               | Monitors the P2Pool daemon log file and creates corresponding events in MongoDb using the MiningDb module.

The modules below are called by the P2Pool module when the corresponding event is detected. These modules extract all historical data for the event, aggregate it into daily totals, writes that data to a CSV file and pushes the file to GitHub where it is rendered by Javascript Apexcharts code.

---

### Export Modules

These modules extract data from MongoDB and transform it. They produce CSV files and use the Db4eGit module to push the files to GitHub.

Module               | Description
---------------------|--------------------------------------
BlocksFoundCsv       | Monero sidechain block found events.
SharesFoundCsv       | Share found events in my mining farm.
SharesFoundByHostCsv | Share found events, by host, in my mining farm.
P2PoolPaymentCsv     | XMR payments made to my mining farm.
Hashrates            | Pool, sidechain and mainchain hashrate data.           | 

---

# Systems Configuration

* [Configuring the Monero Daemon as a Service](/pages/ops/Configuring-the-Monero-Daemon-as-a-Service.html)
* [Configuring the P2Pool Daemon as a Service](/pages/ops/Configuring-the-P2Pool-Daemon-as-a-Service.html)
* [Secondary Monero Daemon Configuration](/pages/ops/Secondary-Monero-Daemon-Configuration.html)
* [Port Forwarding with upnpc](/pages/ops/Port-Forwarding-With-upnpc.html)

---

# Software Build and Install Documentation

* [Building P2Pool from Source](/pages/ops/Building-P2Pool-from-Source.html)
* [Building Monerod from Source](/pages/ops/Building-Monerod-from-Source.html)
* [Installing MongoDB on Debian Linux](/pages/ops/Installing-MongoDB.html)

---

# Hardware

* [Miner CPU and Memory Specs](/pages/ops/Miner-Specs.html)

---

# Links

* [db4e on GitHub](https://github.com/NadimGhaznavi/db4e)
* [Debian Linux](https://www.debian.org/)
* [P2Pool on GitHub](https://github.com/SChernykh/p2pool)
* [Monero on GitHub](https://github.com/monero-project/monero-gui)
* [MongoDB](https://www.mongodb.com/)
* [ApexCharts](https://apexcharts.com/)
* [GitHub](https://github.com/)

