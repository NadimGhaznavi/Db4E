---
layout: post
title: Configuring the P2Pool Daemon as a Service
date: 2025-05-27
---

# Table of Contents

* [Introduction and Scope](#introduction-and-scope)
* [The systemd p2pool.socket definition](#the-systemd-p2pool.socket-definition)
* [The systemd p2pool.service Definition](#the-systemd-p2pool.service-definition)
* [Activing and Enabling the P2Pool Services](#Activing-and-enabling-the-p2pool-services)
* [The P2Pool Daemon Startup Script](#the-p2pool-daemon-startup-script)
* [Credits](#credits)

---

# Introduction and Scope

This page documents the configuration of the P2Pool software used by my Monero mining farm. I have configured P2Pool to connect my collection of machines running XMRig to the Monero Mini Sidechain.

The socket service creates a named pipe that connects the the P2Pool daemon's standard input. This pipe is used to interact with the daemon once it's running. By using this architecture, you can run processes (e.g. a cron script) to send commands to the P2Pool daemon while still running it as a service. The actual P2Pool service definition calls a shell script (shown below) that passes in all the options used to start the P2Pool daemon.

# The systemd p2pool.socket definition

This file is installed in `/etc/systemd/system` and is named `p2pool.socket`. A full listing of the file is shown below:

```
[Unit]
Description=P2Pool Socket

[Socket]
ListenFIFO=/opt/prod/p2pool/p2pool.stdin
RemoveOnStop=true

[Install]
WantedBy=sockets.target
```

# The systemd p2pool.service Definition

This file is installed in `/etc/systemd/system` and is named `p2pool.service`. A full listing of the file is shown below:

```
[Unit]
Description=P2Pool Full Node
After=network.target p2pool.socket
#Requires=monerod.service
BindsTo=p2pool.socket

[Service]
StandardInput=socket
Sockets=p2pool.socket
WorkingDirectory=/opt/prod/p2pool/
Type=simple
Restart=always
ExecStartPre=sysctl vm.nr_hugepages=3072
ExecStart=/opt/prod/p2pool/start-p2pool-mini.sh
TimeoutStopSec=60
StandardOutput=file:/opt/prod/p2pool/p2pool.log
StandardError=file:/opt/prod/p2pool/p2pool.err
[Unit]
Description=P2Pool Full Node
After=network.target p2pool.socket
#Requires=monerod.service
BindsTo=p2pool.socket

[Service]
StandardInput=socket
Sockets=p2pool.socket
WorkingDirectory=/opt/prod/p2pool/
Type=simple
Restart=always
ExecStartPre=sysctl vm.nr_hugepages=3072
ExecStart=/opt/prod/p2pool/start-p2pool-mini.sh
TimeoutStopSec=60
StandardOutput=file:/opt/prod/p2pool/p2pool.log
StandardError=file:/opt/prod/p2pool/p2pool.err

[Install]
WantedBy=multi-user.target

[Install]
WantedBy=multi-user.target
```

# Activing and Enabling the P2Pool Services

To refresh systemd's configuration after creating the service and socket definitions use the command below:

```
sudo systemd daemon-reload
```

To have the P2Pool daemon automatically start at boot time use the command below:

```
sudo systemd enable p2pool.service
```

To actually start the service without rebooting use the command below:

```
sudo systemd start p2pool.service
```

# The P2Pool Daemon Startup Script

I use a shell script to start the P2Pool Daemon. A few points about the startup script:

* The script is not run directly, it's used by a systemd service
* P2Pool is configured to mine on the mini sidechain (the `--mini` switch)
* Be sure to substitute your own Monero wallet address for the WALLET variable
* The `MONERO_NODE` is the IP of a machine that hosts the Monero Blockchain i.e. runs the monerod daemon
* The `ZMQ_PORT` and `RPC_PORT` need to match what the monerod daemon's configuration
* The `P2P_DIR` is the directory where you have the P2Pool software installed

This section shows the start script used to launch P2Pool daemon.

```
#!/bin/bash

# kermit
MONERO_NODE="192.168.0.176"

ANY_IP="0.0.0.0"
STRATUM_PORT=3333
P2P_PORT=38889
ZMQ_PORT=20083
RPC_PORT=20081
P2P_DIR="/opt/prod/p2pool"
WALLET="******************************************************************"
LOG_LEVEL=0
IN_PEERS=10
OUT_PEERS=10
DATA_API_DIR="${P2P_DIR}/json"
P2P_LOG="${P2P_DIR}/p2pool.log"

USER=$(whoami)
if [ "$USER" != "root" ]; then
        echo "ERROR: Run the p2pool daemon as root, exiting.."
        exit 1
fi

./p2pool \
        --host ${MONERO_NODE} \
        --wallet ${WALLET} \
        --mini \
        --stratum ${ANY_IP}:${STRATUM_PORT} \
        --p2p ${ANY_IP}:${P2P_PORT} \
        --rpc-port ${RPC_PORT} \
        --zmq-port ${ZMQ_PORT} \
        --loglevel ${LOG_LEVEL} \
        --in-peers ${IN_PEERS} \
        --out-peers ${OUT_PEERS} \
         | tee -a ${P2P_LOG}
```

# Credits

I authored the wrapper script to actually start P2Pool, but I found the solution to using a named pipe and P2Pool service definition in this [Reddit post](https://www.reddit.com/r/MoneroMining/comments/12w28m6/comment/jhffnn8/?utm_source=share&utm_medium=web2x&context=3&rdt=38081) by [Krewlar](https://www.reddit.com/user/krewlar/). Kudos to [Krewlar](https://www.reddit.com/user/krewlar/) for doing the heavy lifting for this solution.

# Conclusion

That's it! Happy mining!!! :)

