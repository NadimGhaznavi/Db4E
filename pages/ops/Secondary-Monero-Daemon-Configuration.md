---
layout: post
title: Secondary Monero Daemon Configuration 
date: 2025-05-22
---
# Table of Contents

* [Introduction and Scope](#introduction-andscope)
* [Monero Daemon Configuration](#monero-daemon-configuration)
* [Exporting the Blockchain from the Primary Node](#exporting-the-blockchain-from-the-primary-node)
* [Transfer the Blockchain File to the Secondary Node](#transfer-the-blockchain-file-to-the-secondary-node)
* [Elapsed time](#elapsed-time)
* [Importing the Blockchain File on the Secondary Node](#importing-the-blockchain-file-on-the-secondary-node)

# Introduction and Scope

This page documents the configuration of a secondary or backup Monero XMR Service. The idea behind setting up a secondary full Monero node is to handle the case where the primary Monero daemon fails. I have a Monero mining farm that uses a local P2Pool pool which relies on my Monero daemon to be available and serving up the full Monero blockchain. A failure of the Monero daemon means my mining operation is down while I rebuild the monero daemon service. While I can rebuild the OS and rebuild the Monero daemon from source and deploy it in hours, it takes up to two weeks to download the full blockchain from the Internet.

Enter the secondary Monero node hosting a completely independent full instance of the XMR blockchain. 

Because I upgrade the Monero daemon (and other Monero software) whenever there's an update, I have installed the actual blockchain data in a separate directory. When I upgrade the Monero software, I create a new directory to house it (e.g. `/opt/prod/monero-gui-0.18.4.0`). I create a symlink (e.g. `/opt/prod/monerod-gui` and `/opt/prod/monerod`) to point at it (the systemd services reference the symlinks, so those files don't have to be updated when the Monero software is updated) and reference the directory that houses the blockchain data (`/opt/prod/monero-blockchain`) in the Monero daemon startup script.

That's why you'll see me referencing the `monero-blockchain` directory on this page.

# Monero Daemon Configuration

I have documented the process of setting up the Monero Daemon in my [Monero Daemon Configuration](/pages/Monero-Daemon-Configuration.html) page.

# Exporting the Blockchain from the Primary Node

Navigate to the directory housing your Monero daemon and use the `monero-blockchain-export` tool as follows:

```
./monero-blockchain-export --data-dir /opt/prod/monero-blockchain --output-file /opt/prod/maia/2025-05-22_blockchain.raw --log-level 0
```

# Transfer the Blockchain File to the Secondary Node

You can do this in a number of ways. I suggest using `scp` (`man scp`) which is part of the SSH software suite and assumes you have a SSH server running on your target, secondary Monero node:

```
cd /opt/prod/maia
scp 2025-05-22_blockchain.raw maia.osoyalce.com:/tmp
```

I actually used NFS (the /opt/prod/maia directory is a NFS mount), but the scp command above will work as well.

# Elapsed time

I'm not sure where the bottleneck is i.e. if it's the export process or network IO as the target file containing the blockchain export data is on a NFS share. 

```
dan@maia:/exports/maia$ while sleep 1; do ls -lh *raw; sleep 60; done
-rw-r--r-- 1 root root 27M May 22 13:16 2025-05-22_blockchain.raw
-rw-r--r-- 1 root root 39M May 22 13:17 2025-05-22_blockchain.raw
-rw-r--r-- 1 root root 54M May 22 13:18 2025-05-22_blockchain.raw
-rw-r--r-- 1 root root 86M May 22 13:19 2025-05-22_blockchain.raw
-rw-r--r-- 1 root root 116M May 22 13:20 2025-05-22_blockchain.raw
...
...
```

# Importing the Blockchain File on the Secondary Node

TBD



