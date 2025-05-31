---
title: "Building P2Pool from Source"
date: 2025-05-22
markdown: GFM
category:
  - Monero XMR 
  - P2Pool
---
# Table of Contents

* [Introduction and Scope](#introduction-and-scope)
* [Install Pre-Requisites](#install-pre-requisites)
* [Download P2Pool from Github](#download-p2pool-from-github)
* [Configure P2Pool](#configure-p2pool)
* [Build P2Pool](#build-p2pool)
* [Install P2Pool](#build-p2pool)
* [Donations](#donations)
* [Links](#links)

---

# Introduction and Scope

This page documents the process of building [SChernykh's P2Pool Software](https://github.com/SChernykh/p2pool).

---

# Install Pre-Requisites

On my Debian system:
```
sudo apt update
sudo apt install git build-essential cmake libuv1-dev libzmq3-dev libsodium-dev libpgm-dev libnorm-dev libgss-dev libcurl4-openssl-dev libidn2-0-dev
```

---

# Download P2Pool from Github

I keep source code in `/opt/src`. In the example below, the p2pool version is 4.6, be sure to update the directory name (`p2pool-v4.6`) if your version is more recent.

```
cd /opt/src
sudo git clone --recursive https://github.com/SChernykh/p2pool
sudo mv p2pool p2pool-v4.6
```

This clones the SChernykh P2Pool repository into the p2pool directory and renames he directory to reflect the specific version of P2Pool that was downloaded.

---

# Configure P2Pool

Assuming you are building P2Pool version 4.6:

```
cd /opt/src/p2pool-v4.6
sudo mkdir build
cd build
sudo cmake -DWITH_MERGE_MINING_DONATION=OFF ..
```

---

# Build P2Pool

Assuming you are building P2Pool version 4.6:

```
cd /opt/src/p2pool-v4.6/build
NUM_PROCS=4
sudo make -j${NUM_PROCS)
```
-where NUM_PROCS (4 in the example above) is the number of CPU cores you want to dedicate to the build process.

---

# Install P2Pool

I keep custom installed software in `/opt/prod`. I create a version specific directory (e.g. `p2pool-v4.6`) to house the code. I also create a generic symlink that points at the version (e.g. `p2pool`). I reference the symlink in my start/stop scripts when configuring P2Pool as a service (see the [links](#links) section below). When I upgrade P2Pool I do not have to change my start/stop scripts.

```
cd /opt/prod
sudo mkdir p2pool-v4.6
sudo rm -f p2pool
sudo ln -s p2pool-v4.6 p2pool
sudo cp /opt/src/p2pool/build/p2pool /opt/prod/p2pool
```

---

# Donations

SChernykh's Monero XMR wallet address for donations:

```
44MnN1f3Eto8DZYUWuE5XZNUtE3vcRzt2j6PzqWpPau34e6Cf4fAxt6X2MBmrm6F9YMEiMNjN6W4Shn4pLcfNAja621jwyg
```

---

# Links

* [Configuring the P2Pool Daemon as a Service](https://xmr.osoyalce.com/pages/ops/Configuring-the-P2Pool-Daemon-as-a-Service.html)
* [P2Pool on Github](https://github.com/SChernykh/p2pool)
  * [Build Instructions](https://github.com/SChernykh/p2pool/blob/master/README.md#build-instructions)
  * [Disable Auto Donation](https://github.com/SChernykh/p2pool/blob/v4.6/README.md?utm_source=substack&utm_medium=email#donations)

