---
title: Setup db4e as a Service
---

# Introduction

The *db4e* softare monitors the *P2Pool* log and queries the API to gather event and metrics data. Therefore, it's important that *db4e* is always running when *P2Pool* is running so that all events (e.g. a *share found* event) are captured.

The *db4e* service does not require root access, therefore it's configured to use a different account (*sally* in the example below).

This page documents the setup of *db4e* as a *systemd* service.

---

# Pre-Requisites

* I am running [Debian](https://debian.org), but these instructions apply to basically any machine running Linux that uses *systemd*.
* *root* user access.

---

# Setup the Service

## New Service File

Create a *systemd* service file in the `/etc/systemd/system` directory. Name this file `db4e.service` and create it *as the root user*. A complete listing of this file is shown below:

```
[Unit]
Description=DB4E Monitor P2Pool Log Service

[Service]
User=sally
WorkingDirectory=/opt/prod/db4e
ExecStart=/opt/prod/db4e/bin/db4e.sh -m
Restart=always
RestartSec=3
KillMode=process

[Install]
WantedBy=multi-user.target
```

*IMPORTANT NOTE:* The line `User=sally` tells the OS to run the *db4e* service using the *sally* account. You will need to change this to whatever account you've used to install the *db4e* softare.

## Refresh systemd

You need to tell *systemd* that you've changed the configuration of the system.

```
sudo system daemon-reload
```

## Start when Booting

Use the command below to start the *db4e* service automatically when the system boots.

```
sudo systemctl enable db4e
```

# Manual Start

Use the command below to start the service manually:

```
sudo systemctl start db4e
```

# Manual Stop

```
sudo systemctl stop monerod
```

---

# Checking the Status

```
sudo systemctl status monerod
```