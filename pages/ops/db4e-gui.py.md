---
title: db4e-gui.py Console Application
---

The `db4e-gui.py` provides a realtime console based GUI to display health and performance information about my Monero XMR Mining farm. I typically run the application continuously to keep an eye on things.

The application displays the following timestamped information:

* My monero XMR mining farm's wallet balance.
* The hashrate of each cryoptocurrency miner.
* A pane showing the past 11 XMR payments made to the farm.
* A pane showing the past 14 share found events made by the miners.
* An ASCII display of the current share position(s) within the PPLNS (*Pay per last N-Shares*) window.
* The hashrate of the main Monero XMR blockchain.
* The hashrate of the Monero XMR mini sidechain.
* The hashrate of my Mining farm pool.

![Screenshot of db4e-gui.py](/assets/img/db4e-gui.png)

# Pre-Requisites

See the [Pre-Requisites](/pages/ops/Pre-Requisites.html) page for instructions on installing support for the console graphics libraries ([urwid](https://urwid.org/))

# Running the db4e-gui.py Application

Run the `db4e-gui.py` application from within a sandboxed Python enviroment (see [pre-requisites](/pages/ops/Pre-Requisites.html)).

```
. ~/db4e_python
(db4e_python) $ db4e-gui.py
```

[Back](/)



