---
title: Setup the Monero Daemon as a Service
---

# Introduction

This page documents the configuration of the Monero XMR Daemon (*monerod*) as a system service. This ensures that it starts automatically whenever the host computer boots up. The Monero daemon supports interactive commands and to take advantage of this interactive aspect of the daemon I have configured a named pipe or Unix socket that allows for this. With this configuration you can send commands to the Monero daemon by echoing commands into the named pipe.

---

# Pre-Requisites

---

## Linux Operating System

I am running [Debian](https://debian.org), but these instructions apply to basically any machine running
Linux. 

---

## Disk Space Requirements

The disk space required to house the full Monero blockchain is significant. As of the writing of this article, June 2025, the full monero blockchain is 240 Gb. It's recommended that you use a SSD hard-drive, but I'm a using an old-school, magnetic, spinning disk. I migrated from an SSD to this spinning disk and didn't notice any degradation of mining performance.

---

## Monero Software is Installed

The instructions here assume you have the Monero software installed on your system. I have a document on how to download, compile and install the software [here](/pages/ops/Building-Monerod-from-Source.html). This procedure assumes you have the software installed in */opt/prod*:

```
ls -l /opt/prod
total 12
lrwxrwxrwx 1 root root   16 May 27 14:52 monerod -> monerod-0.18.4.0
drwxr-xr-x 4 root root 4096 May 27 14:53 monerod-0.18.4.0
lrwxrwxrwx 1 root root   16 May 27 14:52 monero-gui -> monerod-0.18.4.0
.
.
.
```

---

# The Blockchain Data Files

I keep the actual blockchain data files in a different directory than the *Monero Daemon*. This is referenced by the `--data-dir` switch and the `DATA_DIR` definition in the `start-monerod.sh` script described in the previous section. By keeping the blockchain in a different directory I can download and install a newer version of the *Monero GUI Wallet*, copy in the `start-monerod.sh` script and fire it up without needing to move the 240 Gb file. It also allows you to store that file on another disk mounted on another directory in case you're using a dedicated SSD drive to house the blockchain.

You'll need to create this directory:

```
sudo mkdir /opt/prod/monero-blockchain
```

---

# Setup the Service

The *Monero Daemon* is an interactive process that accepts commands. In order to take advantage of this feature while still running it as a service this implementation uses two distinct services. The primary service is the actual *Monero Daemon*. The secondary service sets up a named pipe which allows the user to send commands to the *Monero Daemon* by echoing commands into the named pipe.

---

## Configuration File

A custom `monerod.ini` file should be created in the `/opt/prod/monerod` directory. This file contains the deployment specific settings for the Monero Daemon. A complete listing is shown below:

```
# Bind to all available network interfaces
IP_ALL="0.0.0.0"

# Port numbers
ZMQ_PUB_PORT="21083"
ZMQ_RPC_PORT="21082"
P2P_BIND_PORT="21080"
RPC_BIND_PORT="21081"

# Peer limits
OUT_PEERS="50"
IN_PEERS="50"

# Log settings
LOG_LEVEL="0"
MAX_LOG_FILES="5"
MAX_LOG_SIZE="100000"
LOG_NAME="monerod.log"

# Not sure
SHOW_TIME_STATS="1"

# Where the Monero software is installed
MONEROD_DIR=/opt/prod/monerod

# Where the blockchain (lmdb directory) is stored
DATA_DIR="/opt/prod/monero-blockchain"

# Trusted Monero nodes to sync off
PRIORITY_NODE_1="kermit.osoyalce.com"
PRIORITY_NODE_1_PORT="20080"
PRIORITY_NODE_2="nodes.hashvault.pro"
PRIORITY_NODE_2_PORT="18080"
```

## Startup Script

The `start-monerod.sh` script reads it's settings from the `monerod.ini` file. this script is not usually called directory. Instead it is called from *systemd*.

A few things to note about this script.

* I run two full monero nodes on my network which are in the same subnet and are behind the
same router. The router supports upnp for routing inbound traffic. In order for the router to
differentiate between the two nodes each node needs to use unique port numbers. The port numbers
I use in the script below are non-standard, the standard port numbers start with *18* (e.g.
`ZMQ_PUB_PORT="18083"`). This isn't really relevant, but is worth mentioning in case you encounter
documentation that talks about slightly different port numbers.
* You'll note that I have *p2pmd.xmrvsbeast* and *nodes.hashvault.pro* configured with the
`--add-priority-hosts` switch. I trust both of these machines and the people who run the 
Monero nodes on these machines. You can safely remove both of these lines if you prefer. 
* You may also notice that the `DATA_DIR` is set to */opt/prod/monero-blockchain* see [The Blockchain Data File](#the-blockchain-data-files) for more info.

```
#!/bin/bash

# Read in the settings
source /opt/prod/monerod/monerod.ini

# Don't allocate large pages
export MONERO_RANDOMX_UMASK=1

# Find the monerod daemon
if [ -d ${MONEROD_DIR} ]; then
	MONERO_DIR=$MONEROD_DIR
	MONEROD=${MONEROD_DIR}/bin/monerod
	if [ ! -x ${MONEROD} ]; then
		echo "ERROR: Unable to locate the monerod daemon (${MONEROD}), exiting..."
		exit 1
	fi
else
	echo "ERROR: Unable to locate the Monero software directory (${MONERO_DIR}), exiting..."
	exit 1
fi

# Set the log name for monerod
LOG_DIR=${MONERO_DIR}/logs
if [ ! -d ${LOG_DIR} ]; then
	mkdir $LOG_DIR
fi
LOG_FILE="${LOG_DIR}/${LOG_NAME}"

# Make sure the blockchain directory exists
if [ ! -d ${DATA_DIR} ]; then
	mkdir -p ${DATA_DIR}
	if [ $? != 0 ]; then
		echo "ERROR: Failed to create blockchain data directory (${DATA_DIR}), exiting..."
		exit 1
	fi
fi

# Launch the monerod daemon
$MONEROD \
	--log-level ${LOG_LEVEL} \
	--max-log-files ${MAX_LOG_FILES} \
	--max-log-file-size ${MAX_LOG_SIZE} \
	--log-file ${LOG_FILE} \
	--zmq-pub tcp://${IP_ALL}:${ZMQ_PUB_PORT} \
	--zmq-rpc-bind-ip ${IP_ALL} --zmq-rpc-bind-port ${ZMQ_RPC_PORT} \
	--p2p-bind-ip ${IP_ALL} --p2p-bind-port ${P2P_BIND_PORT} \
	--add-priority-node=${PRIORITY_NODE_1}:${PRIORITY_NODE_1_PORT} \
	--add-priority-node=${PRIORITY_NODE_2}:${PRIORITY_NODE_2_PORT} \
	--rpc-bind-ip ${IP_ALL} --rpc-bind-port ${RPC_BIND_PORT} --restricted-rpc \
	--confirm-external-bind \
	--data-dir ${DATA_DIR} \
	--out-peers ${OUT_PEERS} --in-peers ${IN_PEERS} \
	--disable-dns-checkpoints --enable-dns-blocklist \
	--show-time-stats ${SHOW_TIME_STATS} \
	--igd enabled \
	--max-connections-per-ip 1 \
	--db-sync-mode safe
```

Once you've created this shell script you'll need to make it executible:

```
sudo chmod a+x /opt/prod/monerod/start-monerod.sh
```

---

## Setup the Daemon Service

The *Monero Daemon Service* is configured as a standard systemd service. To do this 
you need to create a systemd service description file in the `/etc/systemd/system` 
directory. Name this file *monerod.service* and create it as the root user. A complete 
listing of this file is shown below.

```
[Unit]
Description=Monero Daemon Full Blockchain Node
After=network.target monerod.socket
BindsTo=monerod.socket

[Service]
User=db4e
StandardInput=socket
Sockets=monerod.socket
WorkingDirectory=/opt/prod/monerod/
Type=simple
Restart=always
ExecStart=/opt/prod/monerod/start-monerod.sh
TimeoutStopSec=60
StandardOutput=file:/opt/prod/monerod/logs/monerod.log
StandardError=file:/opt/prod/monerod/logs/monerod.err

[Install]
WantedBy=multi-user.target
```

---

## Setup the Socket Service

This file is installed in `/etc/systemd/system` and is named `monerod.socket`. A full listing of the file is shown below:

```
[Unit]
Description=Monerod Stdin Socket













[Socket]
User=db4e
ListenFIFO=/opt/prod/monerod/run/monerod.stdin
RemoveOnStop=true

[Install]
WantedBy=sockets.target
```

Note that the named pipe is called `/opt/prod/monerod/monerod.stdin`. To send commands to the
*Monero Daemon* simply echo the command and direct the output into this named pipe. The 
shell command below shows an example:

```
echo status > /opt/prod/monerod/monerod.stdin
```

If you look at the previous section where we defined the *Monero Daemon* service, you will
see that it includes a `StandardOutput` directive. The results of the command (e.g. status)
will show up in this file.

---

## Refresh systemd 

In order to let *systemd* know about these newly created services i.e. monerod.service and
monerod.socket you need to issue the command below:
```
sudo systemd daemon-reload
```

---

## Start when Booting

To have *systemd* automatically start the *Monero Daemon* whenever your system boots, simply
execute the command below:

```
sudo systemd enable monerod.service
```

That's it! You're done! You can safely reboot the server to confirm that the Monero daemon starts up automatically at boot time. Check the */opt/prod/monerod/logs/monerod.log* file for logging information.

---

# Manual Starts

You can also start the service without rebooting:

```
sudo systemctl start monerod
```

---

# Manual Stops

```
sudo systemctl stop monerod
```

---

# Checking the Status

```
sudo systemctl status monerod
```
