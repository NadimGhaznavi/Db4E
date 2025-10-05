---
title: The Database 4 Everything
layout: default
---

# Welcome

This is the home of **Db4E**, the **Database 4 Everything** project — A unified Monero XMR mining dashboard for deployment, operation and real-time analytics.

Db4E aims to be simple enough for new miners and flexible enough for advanced users. It’s still under active development, but the foundations are solid — and thanks to the [Textual Rapid Application Framework](https://textual.textualize.io/), progress is astonishingly fast.

**Now available on [PyPI](https://pypi.org/project/db4e/):**  

```shell
pip install db4e
```

---

# Features Today

* 🎉 PyPI releases — You can `pip install db4e` to install *Db4E*!
* 🛠️ Deployment manager with smooth vendor directory handling and update workflows.
* 🖥️ Fully integrated Textual-based TUI with interactive forms — no more manual command-line configs.
* 🔒 Built-in security architecture with sudoers-based privilege management.
* 🧩 Modular design for future-proof upgrades of Monerod, P2Pool, and XMRig.
* ✅ Active development in Git branches, keeping `main` clean and stable.
* 📚 View Monero, P2Pool, XMRig logs in the TUI.
* 📈 Historical hashrate miner, pool and chain data plots.
* ⚙️ Pre-populated configuration forms for Monero, P2Pool, and XMRig to get you up and running fast!
* 🔍 Start/stop log and cumulative uptime reports for Monero, P2Pool, XMRig and more.
* 🚀 Seamless integration with `systemd` and `logrotate`

---

# MongoDB Backend

Db4E uses a **MongoDB backend** to store historical mining data, logs, and configuration. The Db4E service runs continuously, monitors P2Pool logs and API responses, and writes structured records into MongoDB. [Interactive TUI](/pages/db4e-tui.py.html) that serves as a unified Monero XMR mining dashboard for deployment, operation and real-time analytics.

See the [Mongo Community Edition Install HOWTO](/pages/Installing-MongoDB.html) for step-by-step instructions.

---

# Technology Stack

Db4E runs on [Debian Linux](https://www.debian.org/) and includes the following core components:

* [Db4E core application](https://github.com/NadimGhaznavi/Db4E) — built with the [Textual](https://textual.textualize.io/) RAD framework.
* [Monero Daemon (monerod)](https://www.getmonero.org/).
* [P2Pool daemon](https://github.com/SChernykh/p2pool).
* [XMRig](https://xmrig.com/) mining software.
* [MongoDB](https://www.mongodb.com/) for historical data storage.
* [systemd](https://en.wikipedia.org/wiki/Systemd) for service management.
* [logrotate](https://www.logrotate.org/) for log file management.
* *Terminal User Interface* based on [Textual](https://textual.textualize.io/).

The [Architecture](/pages/Architecture.html) page provides additional detail on the internals of **Db4E**. The page is a work in progress.

---

# Release Management

For details on how development and releases are managed, see the [Git Branching Strategy](/pages/Git-Branching-Strategy.html) and the [Git Commit Standard](/pages/Git-Commit-Standard.html).

---

# Getting Started

Refer to the [Getting Started](pages/Getting-Started.html) for detailed step on deploying Db4E.

---

# Coming Soon

* 📢  PyPI release checking — automatic version notifications.
* 🔒  Full security architecture documentation.
* 🐞  Full unit + integration testing suite and CI/CD integration.
* 🕵️  Community building and open contributions — feedback welcomed!

---

# Community Feedback

*Questions? Ideas? Feedback?* Please go to the *db4e* project's [Discussions](https://github.com/NadimGhaznavi/db4e/discussions) page or checkout my [Blog](https://blog.osoyalce.com/).

---

# Donations

If you find Db4E useful, please consider [donating](/pages/Donations.html) to help support its ongoing development. Every contribution helps!


