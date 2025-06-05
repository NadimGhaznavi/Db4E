---
title: The Database 4 Everything
layout: default
---
<script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.0/papaparse.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
<script src="/assets/js/sharesfound/by-miner-sharesfound-30days.js"></script>

# Mining Monero XMR

<div id="wrapper">
  <div id="areaChart">
  </div>
  <div id="barChart">
  </div>
 </div>

This is the home of the **db4e**, the **Database 4 Everything**  project. The **db4e** application provides a [console based dashboard](/pages/ops/db4e-gui.py.html), and historical [web reports](#web-reports) to monitor your miners, your pool and the Monero ecosystem.

---

# Monitoring

The db4e [console application](/pages/ops/db4e-gui.py) is a command line utility that displays the following information:

 * Mining wallet balance
 * Worker hashrates
 * Hashrates of your local pool, the sidechain, and the Monero mainchain
 * Recent shares found in your local pool (inluding timestamp and miner who found the share)
 * Recent payments made to your mining operation

The console application gets the data from the and updates once a minute.

---

# Web Reports

Reporting with *db4e* is easy. A reports definition file tells *db4e* what kinds of reports to prepare.

* Reports are published to the web
* Reports are defined in a simple YAML file format
* Reports can be scheduled (e.g. [pool hashrate](/pages/reports/hashrates/Pool-Hashrate-60-Days.html) reports)
* Some reports in *db4e* are event driven (e.g. [recent payments](/pages/reports/payments/Daily-Payment-60-Days.html) reports)
* Reports can be run manually

The [Reports](/pages/web/Reports.html) page has links to currently configured reports.

---

# Data Warehouse

The *db4e* stands out from other Monero XMR software in that it includes a **Data Warehouse**. The *db4e* application is setup as a system service. When running it monitors the local P2Pool software and creates records in the backend datastore. The data warehouse is used to genereate [reports](/pages/web/Reports.html) and as a data source for the [db4e console application](/pages/ops/db4e-gui.py.html).

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

# Systems Architecture

The application is designed to be modular and have a clear data abstraction layer. Mining database operations go though a *mining
database class* which sends those to a *db4e mining class* which interacts with MongoDB.

For example, mining data exports to CSV are performed by connecting to the *MiningDb* class which connects to the *Db4eDb* class which connects to MongoDb and fetches the data.

---

# Codebase Architecture

See the [Codebase Architecture](/pages/ops/Codebase-Architecture.html) page for more information.

---

# Utilities

Utilities include the core [db4e.py](/pages/ops/db4e.py.html) too, the [db4e-gui.py](/pages/ops/db4e-gui.py.html) console application, the [backup-db.sh](/pages/ops/backup-db.sh.html) and more.

See the [Utilities](/pages/ops/Utilities.html) for a comprehensive list.

---

# Systems Configuration

* [Setup the Monero Daemon as a Service](/pages/ops/Setup-the-Monero-Daemon-as-a-Service.html)
* [Setup the P2Pool Daemon as a Service](/pages/ops/Setup-the-P2Pool-Daemon-as-a-Service.html)
* [Secondary Monero Daemon Configuration](/pages/ops/Secondary-Monero-Daemon-Configuration.html)
* [Port Forwarding with upnpc](/pages/ops/Port-Forwarding-With-upnpc.html)

---

# 3rd Party Software 

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









