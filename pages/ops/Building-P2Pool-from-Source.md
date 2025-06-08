---
title: "Building P2Pool from Source"
---

# Introduction

This page documents the process of building [SChernykh's P2Pool Software](https://github.com/SChernykh/p2pool).

---

# Deployment Architecture

See the [Deployment Architecture](/pages/ops/Deployment-Architecture.html) for information on how the source, build and install directories are orgainized for this process.

---

# Install Pre-Requisites

On my Debian system:
```
sudo apt update
sudo apt install git build-essential cmake libuv1-dev libzmq3-dev libsodium-dev libpgm-dev libnorm-dev libgss-dev libcurl4-openssl-dev libidn2-0-dev
```

---

# Download the Source Code

I keep source code in `/opt/src`. In the example below, the p2pool version is 4.6, be sure to update the directory name (`p2pool-v4.6`) if your version is more recent.

```
cd /opt/src
sudo git clone --depth 1 --recursive https://github.com/SChernykh/p2pool
sudo mv p2pool p2pool-v4.6
```

This clones the SChernykh P2Pool repository into the p2pool directory and renames he directory to reflect the specific version of P2Pool that was downloaded.

---

# Configure and Build 

Assuming you are building P2Pool version 4.6:

```
cd /opt/src/p2pool-v4.6
sudo mkdir build

sudo cmake --install-prefix=/opt/prod/p2pool-v4.6 -DWITH_MERGE_MINING_DONATION=OFF
```

---

# Build and Install P2Pool
 
Assuming you are building P2Pool version 4.6:

```
cd /opt/src/p2pool-v4.6/build
NUM_PROCS=4
sudo make -j${NUM_PROCS)
sudo make install
```

-where NUM_PROCS (4 in the example above) is the number of CPU cores you want to dedicate to the build process.

I keep custom installed software in `/opt/prod`. I create a version specific directory (e.g. `p2pool-v4.6`) to house the code. I also create a generic symlink that points at the version (e.g. `p2pool`). I reference the symlink in my start/stop scripts when configuring P2Pool as a service (see the [links](#links) section below). When I upgrade P2Pool I do not have to change my start/stop scripts.

```
cd /opt/prod
sudo rm -f p2pool
sudo ln -s p2pool-v4.6 p2pool
```

```
NOTE:
-- Installing: /usr/local/lib/libz.so.1.3
-- Installing: /usr/local/lib/libz.so.1
-- Installing: /usr/local/lib/libz.so
-- Installing: /usr/local/lib/libz.a
-- Installing: /usr/local/include/zconf.h
-- Installing: /usr/local/include/zlib.h
-- Installing: /usr/local/share/man/man3/zlib.3
-- Installing: /usr/local/share/pkgconfig/zlib.pc
```
---

---

# Links

* [Configuring the P2Pool Daemon as a Service](/pages/ops/Configuring-the-P2Pool-Daemon-as-a-Service.html)
* [P2Pool on Github](https://github.com/SChernykh/p2pool)
  * [Build Instructions](https://github.com/SChernykh/p2pool/blob/master/README.md#build-instructions)
  * [Disable Auto Donation](https://github.com/SChernykh/p2pool/blob/v4.6/README.md?utm_source=substack&utm_medium=email#donations)









