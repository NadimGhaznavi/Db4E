---
title: "Building Monerod from Source"
---

# Table of Contents

* [Introduction and Scope](#introduction-and-scope)
* [Install Pre-Requisites](#install-pre-requisites)
* [System Architecture](#system-architecture)
* [Download the Source Code from Github](#download-the-source-code-from-github)
* [Configure and Build the Software](#configure-and-build-the-software)
* [Install the Software](#install-the-software)
* [Configuring the Monero Daemon as a Service](#configuring-the-monero-daemon-as-a-service)
* [Links](#links)

---

# Introduction and Scope

This page documents the process of downloading, configuring and installing the core Monero software. The specific directories referenced here are consistent with the [system architecture](#system-architecture) outlined below.

This is the authoritative Monero core software which includes the following:

```
monero-blockchain-ancestry	      monero-blockchain-prune			monero-gen-ssl-cert
monero-blockchain-depth		      monero-blockchain-prune-known-spent-data	monero-gen-trusted-multisig
monero-blockchain-export	      monero-blockchain-stats			monero-wallet-cli
monero-blockchain-import	      monero-blockchain-usage			monero-wallet-gui
monero-blockchain-mark-spent-outputs  monerod
```

As well as the following static libraries:
```
libwallet.a  libwallet_api.a
```

---

# Install Pre-Requisites

Use the command below to install the pre-requisites required to build the software.

```
sudo apt install git build-essential cmake miniupnpc libunbound-dev graphviz doxygen libunwind8-dev pkg-config libssl-dev libzmq3-dev libsodium-dev libhidapi-dev libnorm-dev libusb-1.0-0-dev libpgm-dev libprotobuf-dev protobuf-compiler libgcrypt20-dev libboost-chrono-dev libboost-date-time-dev libboost-filesystem-dev libboost-locale-dev libboost-program-options-dev libboost-regex-dev libboost-serialization-dev libboost-system-dev libboost-thread-dev
```

While this document is focused on the Monero Daemon, the software we're installing includes the official Monero wallet GUI. To ensure a successful compile, you'll also need to install supporting Qt libraries for displaying the GUI:

```
sudo apt install qtbase5-dev qtdeclarative5-dev qml-module-qtqml-models2 qml-module-qtquick-controls qml-module-qtquick-controls2 qml-module-qtquick-dialogs qml-module-qtquick-xmllistmodel qml-module-qt-labs-settings qml-module-qt-labs-platform qml-module-qt-labs-folderlistmodel qttools5-dev-tools qml-module-qtquick-templates2 libqt5svg5-dev
```

---

# System Architecture

Systems architectures vary dramatically, the architecture described here is just one example. This is Linux, so there's always more than one way to do it.

---

## Source Code Management

I keep all source code in a custom `/opt/src` directory. The `/opt` directory is standard on UNIX and should exist on any Linux system.

```
sudo mkdir /opt/src
```

---

## Production Code Management

I keep third party and code that I build myself in `/opt/prod`.

```
sudo mkdir /opt/prod
```

---

# Download the Source Code from Github

I am installing version **0.18.4.0** of the software. The directory name I use reflects that specific version. You may need to change this if you are working with a newer version.

```
cd /opt/src
sudo git clone --recursive https://github.com/monero-project/monero-gui
sudo mv monero-gui monerod-0.18.4.0
```

---

# Configure and Build the Software

Assuming you are using the directory names that were used in the section above:

```
cd /opt/src/monerod-0.18.4.0
sudo make release -j4
```

The `-j4` flag tells `make` to use 4 CPU cores when doing the build. You may want to change this to a different number (or leave it out entirely to use only 1 core) depending on how many CPU cores you have available. I get some warnings when compiling, I'm assuming these are safe to ignore. 

---

# Install the Software

As mentioned in the [production code management section](#production-code-management) above, I install custom software in `/opt/prod`

Create a directory to house the software, note that the instuctions include the version number of the software. You may need to change this if you are compiling a later version.

## Create the Target Install Directory

```
sudo mkdir /opt/prod/monerod-0.18.4.0
sudo rm -f /opt/prod/monerod
sudo rm -f /opt/prod/monero-gui
cd /opt/prod
sudo ln -s monerod-0.18.4.0 monerod
sudo ln -s monerod-0.18.4.0 monero-gui
```

As you can see from the commands above, I have created two symlinks, `monerod` and `monero-gui` that point at the new installation directory. Using symlinks means I can reference them in start/stop scripts and in my Linux PATH environment environment. This means that I do **not** have to modify the start/stop scripts or my PATH when I upgrade the software.

## Actually Install the Software

Assuming you are using the same paths as outlined in this document:

```
sudo cp -a /opt/src/monerod-0.18.4.0/build/release/bin /opt/prod/monerod
sudo cp -a /opt/src/monerod-0.18.4.0/build/release/lib /opt/prod/monerod
```

---

# Configuring the Monero Daemon as a Service

See my [Configuring the Monero Daemon as a Service](/pages/Configuring-the-Monero-Daemon-as-a-Service.html) page for detailed instructions on setting this up.

---

# Links

* My [Configuring the Monero Daemon as a Service](/pages/Configuring-the-Monero-Daemon-as-a-Service.html)
* Official [Monero Software on Github](https://github.com/monero-project/monero-gui)
  * Official [Build Instructions](https://github.com/monero-project/monero-gui?tab=readme-ov-file#compiling-the-monero-gui-from-source)







