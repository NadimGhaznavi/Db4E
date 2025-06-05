---
title: "Pre-Requisites for db4e Installation"
---

# MongoDB

See [Installing MongoDB on Debian Linux](/pages/ops/Installing-MongoDB.html).

# P2Pool

* [Building P2Pool from Source](/pages/ops/Building-P2Pool-from-Source.html)
* [Configuring the P2Pool Daemon as a Service](/pages/ops/Configuring-the-P2Pool-Daemon-as-a-Service.html)

# Monero Daemon

Your P2Pool daemon needs a Monero node. Use these procedures to build and deploy your own full Monero node.

* [Building Monerod from Source](/pages/ops/Building-Monerod-from-Source.html)
* [Configuring the Monero Daemon as a Service](/pages/ops/Configuring-the-Monero-Daemon-as-a-Service.html)

# Console Graphics Support

## Python3 Sandbox Support

The sandbox lets you install additional Python libraries without polluting your host system's Python installation.

```
apt install python3.11-venv
apt install python3-pip
python3 -m venv ~/db4e_python
```

This will install db4e python into your home directory in the `db4e_python` directory.

## Console Graphics Libary Installation

Urwid is used for the graphical console support framework.
```
. ~/db4e_python/bin/activate
(db4e_python) $ pip install install urwid
```

## Running Console Graphics Programs

```
. ~/db4e_python/bin/activate
(db4e_python) $ db4e-gui.py
```













