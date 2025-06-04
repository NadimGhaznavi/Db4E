---
title: Console Application
---

# Console Application

The *db4e-gui.py* provides a realtime console based GUI to display health and performance information about the Monero XMR Mining farm.

![Screenshot of db4e-gui.py](/assets/images/db4e-gui.png)

# Pre-Requisites

## Sandbox Setup

The sandbox lets you install additional Python libraries without polluting your host system's Python installation.

```
apt install python3.11-venv
apt install python3-pip
python3 -m venv ~/db4e_python
```

## Library Install

Urwid is used for the graphical console support framework.
```
. ~/db4e_python/bin/activate
(db4e_python) $ pip install install urwid
```

# Usage

Run the `db4e-gui.py` application from within a sandboxed Python enviroment.

```
. ~/db4e_python
(db4e_python) $ db4e-gui.py
```

[Back](/)



