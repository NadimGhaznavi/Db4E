---
title: "Building XMRig from Source"
---

# Introduction

This page documents the process of building [XMRig](https://github.com/xmrig/xmrig).

---

# Deployment Architecture

See the [Deployment Architecture](/pages/ops/Deployment-Architecture.html) for information on how the source, build and install directories are orgainized for this process.

---

# Install Pre-Requisites

On Debian:

```
sudo apt update
sudo apt install git build-essential cmake libuv1-dev libzmq3-dev libsodium-dev libpgm-dev \
libnorm-dev libgss-dev libcurl4-openssl-dev libidn2-0-dev libhwloc15
```

**NOTE:** The hwloc15 library is required to run the *xmrig* being built here.

---

# Build Script

```
#!/bin/bash
#
# Script to build XMRig
#
XMRIG_VERSION=xmrig-v3.0.0
ENVIRON=qa
LOG=${XMRGIG_VERSION}.log

# The final XMRig binary
XMRIG=xmrig
# Where the source code is
SRC_DIR=/opt/src/${XMRIG_VERSION}
# Where the software will be installed
INSTALL_DIR=/opt/${ENVIRON}/${XMRIG_VERSION}

# Configure the source 
#
echo "CONFIGURING THE SOURCE" | tee ${LOG}
cmake  --install-prefix=${INSTALL_DIR} ${SRC_DIR} | tee -a ${LOG}

# Build the software with NUM_PROCS threads
NUM_PROCS=6
echo "BUILDING THE SOFTWARE" | tee -a ${LOG}
make -j${NUM_PROCS} | tee -a ${LOG}

# Copy the binary to the install target
if [ ! -d ${INSTALL_DIR}/bin ]; then
	mkdir -p ${INSTALL_DIR}/bin
fi
echo -n "INSTALLING THE SOFTWARE" | tee -a ${LOG}
cp ${XMRIG} ${INSTALL_DIR}/bin 
echo "DONE: xmrig installed in ${INSTALL_DIR}/bin"
```