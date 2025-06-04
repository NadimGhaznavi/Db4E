---
title: The Database 4 Everything
layout: default
---
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
<script src="/assets/js/SharesFoundByHostShort.js"></script>

# Mining Monero XMR

<div id="wrapper">
  <div id="areaChart">
  </div>
  <div id="barChart">
  </div>
 </div>

This is the home of the **db4e**, the **Database 4 Everything**  project. The **db4e** application is used to provide a [console based dashboard](/pages/ops/db4e-gui.py.html), [realtime web based visualizations](/pages/web/index.html) and [custom scheduled reports](#custom-scheduled-reports) to monitor a local Monero XMR Mining farm using a local P2Pool node. 

---

# Console Application

The db4e [console application](/pages/ops/db4e-gui.py) is a command line utility that displays the following information:

 * Mining wallet balance
 * Worker hashrates
 * Hashrates of your local pool and the Monero mainchain and sidechain
 * Recent shares found in your local pool (inluding timestamp and miner who found the share)
 * Recent payments made to your mining operation

The console application gets the data from the [data warehouse](#data-warehouse) and updates once a minute.

---

# Web Reports

Reporting with *db4e* is easy:

* Reports are defined in a simple YAML file format
* Reports can be scheduled (e.g. [hashrate of the mini sidechain for the last 90 days](/pages/reports/hashrate/Sidechain-Hashrate-90-Days.html))
* Some reports in *db4e* are event driven (e.g. [recent payments](/pages/reports/payment/Daily-Payment-30-Days.html) reports). 
* Reports can be run manually

* [Daily](/pages/reports/payments/Daily-Payment-90-Days.html) and [cumulative](/pages/reports/payments/Cumulative-Payment-90-Days.html) XMR payments made to the mining farm
* [Shares found](/pages/web/Shares-Found-Short.html) and the colorful [shares found by host](/pages/web/Shares-Found-by-Host-Short.html) by the mining farm
* [Blocks found](/pages/reports/blocksfound/Blocksfound-90-Days.html) on the Monero XMR mini sidechain

The [Reports] page has links to configured reports.

---

# Data Warehouse

The *db4e* stands out from other Monero XMR software in that it includes a **Data Warehouse**. The *db4e* application is setup as a system service. When running it monitors the local P2Pool software and creates records in the backend datastore. The data warehouse is used to genereate [reports](#automated-web-reports) and as a data source for the [db4e console application](/pages/ops/db4e-gui.py.html).

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

# Architecture

The application is designed to be modular and have a clear data abstraction layer. Mining database operations go though a *mining
database class* which sends those to a *db4e mining class* which interacts with MongoDB.

For example, mining data exports to CSV are performed by connecting to the *MiningDb* class which connects to the *Db4eDb* class which connects to MongoDb and fetches the data.

---

## Utilities

---

### db4e.py

This utility monitors the Mining Farm's P2Pool daemon logs, creates records in the backend database and triggers updates to the web front end. See the [db4e.py page](/pages/ops/db4e.py.html) for more information.

---

### db4e-gui.py

The *db4e-gui.py* application provides a console based monitoring solution for my Monero XMR Mining farm.See the [db4e-gui.py page](/pages/ops/db4e-gui.py.html) for more information.

---

### backup-db.sh

The *backup-db.sh* utility is used to backup the backend MongoDB database. The database contains all of the historical data that the [db4e.py](/pages/ops/db4e.py.html) application collects. See the [backup-db.sh page](/pages/ops/backup-db.sh.html) for more information.

---

### db4e-git.sh

The *db4e-git.sh* utility is responsible for pushing files to GitHub where they are picked up by the JavaScript code and rendered into graphs and bar charts.

---

### db4e-restart.sh

The *db4e-restart.sh* script executed once a day from a cron job. It performs the following sequenced actions:

1. Restart the Monero XMR daemon which is responsible for running the full blockchain node. The node is part of the larger, distributed Monero XMR ecosystem.
2. Restart my Mining Farm's P2Pool daemon.
3. Restart the *db4e* P2Pool log file monitoring daemon.

Additionally, each miner also has a cron job to restart the `xmrig` mining software. Best practice is to restart on a scheduled basis.

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
P2Pool               | Monitors the P2Pool log, queries the API and creates corresponding events in MongoDb using the MiningDb module.
MiningReports        | Parses the reports definition files, generates CSV, Javascript and GitHub markdown files and publishes to GitHub Pages.

---

## JavaScript

Javascript files for the different report types have been written. These render the CSV data into plots such as bar charts and area graphs.

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





