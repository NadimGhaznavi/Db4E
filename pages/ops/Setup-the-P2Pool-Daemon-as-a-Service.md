---
title: Setup the P2Pool Daemon as a Service
---

# Introduction

This page documents the configuration of the *P2Pool* software used by my Monero mining farm. I have configured *P2Pool* to connect my collection of machines running *XMRig* to the *Monero Mini Sidechain*.

The socket service creates a named pipe that connects the the P2Pool daemon's standard input. This pipe is used to interact with the daemon once it's running. By using this architecture, you can run processes (e.g. a cron script) to send commands to the P2Pool daemon while still running it as a service. The actual P2Pool service definition calls a shell script (shown below) that passes in all the options used to start the P2Pool daemon.

---

# Pre-Requisites

---

## Linux Operating System

I am running [Debian](https://debian.org), but these instructions apply to basically any machine running Linux. 

---

## P2Pool Software is Installed

The instructions here assume you have the P2Pool software installed on your system. I have a document on how to download, compile and install the software [here](/pages/ops/Building-P2Pool-from-Source.html). This procedure assumes you have the software installed in */opt/prod*:

```
ls -l /opt/prod
total 12
lrwxrwxrwx  1 root  root     11 May 22 22:58 p2pool -> p2pool-v4.6
drwxr-xr-x  7 root  root   4096 May 31 17:33 p2pool-v4.6
```

# Setup the Service

The *P2Pool Daemon* is an interactive process that accepts commands. In order to take advantage of this feature while still running it as a service this implementation uses two distinct services. The primary service is the actual *P2Pool Daemon*. The secondary service sets up a named pipe which allows the user to send commands to the *P2Pool Daemon* by echoing commands into the named pipe.

---

## Configuration File

This file should be created in the `conf` directory where you installed P2Pool (e.g. `/opt/prod/p2pool-v4.6/conf`). A complete listing is shown below.

```
# Where the mining payouts should be sent
WALLET="48wY7nYBsQNSw7v4LjoNnvCtk1Y6GLNVmePGrW82gVhYhQtWJFHi6U6G3X5d7JN2ucajU9SeBcijET8ZzKWYwC3z3Y6fDEG"

# Set the P2Pool base directory.
P2P_DIR=/opt/prod/p2pool

# Configure access to the Monero Daemon that hosts the blockchain
MONERO_NODE="192.168.0.176"
ZMQ_PORT=20083  # NOTE: The standard port is 18083
RPC_PORT=20081  # NOTE: The standard port is 18081

# P2Pool settings
ANY_IP="0.0.0.0"
STRATUM_PORT=3335
P2P_PORT=38890
LOG_LEVEL=1
IN_PEERS=16
OUT_PEERS=16
```

---

## Startup Script

I use a shell script to start the P2Pool Daemon. A few points about the startup script:

* The script is not run directly, it's used by a systemd service.
* P2Pool is configured to mine on the mini sidechain (the `--mini` switch).
* The script reads it's settings from a `p2pool.ini` file.
* Be sure to substitute your own Monero wallet address for the `WALLET` variable in the `p2pool.ini` file.
* The `MONERO_NODE` is the IP of a machine that hosts the Monero Blockchain i.e. runs the monerod daemon
  * The `ZMQ_PORT` and `RPC_PORT` need to match what the monerod daemon's configuration
* The `P2P_DIR` is the directory where you have the P2Pool software installed

A complete listing is shown below. It should be installed in the `bin` directory that's within the P2Pool installation directory (e.g. `/opt/prod/p2pool-v4.6/bin`).

```
#!/bin/bash

# Read in the P2Pool settings
source /opt/prod/p2pool/conf/p2pool.ini## The p2pool.ini File

# Setup sub-directories
API_DIR=${P2P_DIR}/api
RUN_DIR=${P2P_DIR}/run
LOG_DIR=${P2P_DIR}/logs
BIN_DIR=${P2P_DIR}/bin

# P2Pool daemon log file
P2P_LOG="${LOG_DIR}/p2pool.log"
# The P2Pool daemon
P2POOL="${BIN_DIR}/p2pool"

# Create the API directory if it doesn't already exist
if [ ! -d $API_DIR ]; then
  mkdir ${API_DIR}
fi

# Create the run directory if it doesn't already exist
if [ ! -d ${RUN_DIR} ]; then
	mkdir -p ${RUN_DIR}
fi

# Create the logs directory if it doesn't already exist
if [ ! -d ${LOG_DIR} ]; then
	mkdir -p ${LOG_DIR}
fi

# Actually start P2Pool
$P2POOL \
	--host ${MONERO_NODE} \
	--wallet ${WALLET} \
	--mini \
	--no-color \
	--stratum ${ANY_IP}:${STRATUM_PORT} \
	--p2p ${ANY_IP}:${P2P_PORT} \
	--rpc-port ${RPC_PORT} \
	--zmq-port ${ZMQ_PORT} \
	--loglevel ${LOG_LEVEL} \
	--in-peers ${IN_PEERS} \
	--out-peers ${OUT_PEERS} \
	--data-api ${API_DIR}
```

---

## Setup the Daemon Service

This file is installed in `/etc/systemd/system` and is named `p2pool.service`. A full listing of the file is shown below:

```
[Unit]
Description=P2Pool Full Node
After=network.target p2pool.socket
#Requires=monerod.service
BindsTo=p2pool.socket

[Service]
User=db4e
StandardInput=socket
Sockets=p2pool.socket
WorkingDirectory=/opt/prod/p2pool/
Type=simple
Restart=always
ExecStartPre=sysctl vm.nr_hugepages=3072
ExecStart=/opt/prod/p2pool/bin/start-p2pool.sh
TimeoutStopSec=60
StandardOutput=file:/opt/prod/p2pool/logs/p2pool.log
StandardError=file:/opt/prod/p2pool/logs/p2pool.err

[Install]
WantedBy=multi-user.target
```

---

## Setup the Socket Service

This file is installed in `/etc/systemd/system` and is named `p2pool.socket`. A full listing of the file is shown below:

```
[Unit]
Description=P2Pool Socket

[Socket]
User=db4e
ListenFIFO=/opt/prod/p2pool/run/p2pool.stdin
RemoveOnStop=true

[Install]
WantedBy=sockets.target
```

---

## Refresh systemd

To refresh systemd's configuration after creating the service and socket definitions use the command below:

```
sudo systemd daemon-reload
```

To have the P2Pool daemon automatically start at boot time use the command below:

```
sudo systemd enable p2pool.service
```

That's it! You're done! You can safely reboot the server to confirm that the Monero daemon starts up automatically at boot time. Check the `/opt/prod/p2pool/logs/p2pool.log` file for logging information.

---

# Manual Starts

You can also start the service without rebooting:

```
sudo systemd start p2pool
```

---

# Manual Stops

```
sudo systemctl stop p2pool
```

---

# Checking the Status

```
sudo systemctl status p2pool
```

---

# Credits

I authored the wrapper script to actually start P2Pool, but I found the solution to using a named pipe and P2Pool service definition in this [Reddit post](https://www.reddit.com/r/MoneroMining/comments/12w28m6/comment/jhffnn8/?utm_source=share&utm_medium=web2x&context=3&rdt=38081) by [Krewlar](https://www.reddit.com/user/krewlar/). Kudos to [Krewlar](https://www.reddit.com/user/krewlar/) for doing the heavy lifting for this solution.









