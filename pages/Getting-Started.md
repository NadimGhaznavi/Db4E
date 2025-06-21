---
title: Getting Started
---

# Introduction

This page will guide you through the process of setting up the *Database 4 Everything* on your system.

---

# Pre-Requisites

## Debian Linux

While *db4e* is certified for [Debian](https://debian.org) [12 Bookworm](https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.11.0-amd64-netinst.iso) Linux, it should work with minimal tweaks on any Linux distribution.

This guide assumes a *minimal* Debian (NetInst) install with only:

  * SSH server
  * Standard system utilities

-selected.

## Additional Software

Some standard packages are required to setup and run *db4e*:

```
sudo apt-get install gnupg curl libhwloc15 rsync python3.11-venv libzmq5 pip
```

* The *gnupg* and *curl* packages are needed to install MongoDB
* The *libhwloc15* package is required to run XMRig
* *rsync* is used by the `db4e-update-repo.sh` script
* The *python3.11-venv* and *pip* packages are required to install the db4e Python venv environment
* The *libzmq5* package is required to run P2Pool

## Root Access

The *db4e* application does *NOT* require root access to run. However, root access is required to:

* Install Pre-Requisite Linux packages
* Install MongoDB
* Run the XMRig miner 
* Configure *db4e* as a system service

You will only be required to use the root password when you install the package pre-requisites and to install the *db4e* service. For optimal performance, the included XMRig miner needs to access Model-Specific Registers (MSRs). This requires root access. To handle this *db4e* sets the SUID bit on the XMRig binary.

The *db4e* applicaiton **NEVER** stores the root password.

### Dedicated db4e Account

**PRO TIP:** The *best practise* is to created a dedicated Linux *db4e* account named `db4e`. Have that account own the *db4e* code and the *GitHub Pages* repository. This is optional.

---

# Install MongoDB 

MongoDB does not ship with Debian, however the good folks at Mongo run their own repository. See [Installing MongoDB](/pages/Installing-MongoDB.html) for detailed instructions on setting up repository access and installing MongoDB.

---

# Create a GitHub Account

If you don't already have one, you can get a free GitHub account.

* Navigate to [https://github.com](https://github.com) and click on the *Sign up* button.

---

# Create a Repository

Next you'll need to create a GitHub repository. This will host the *db4e* website.

* Navigate to [https://github.com](https://github.com) and click on the *Sign in* button.
* Once you've signed in, click on your account icon in the top-right corner to access the drop down menu. 
* Click on *Your repositories* menu item
* On the *Repositories* page click on the *New* button.
* Choose a name for your repository, e.g. *xmr*.
* Add a description, e.g. *Monero XMR Mining Farm*
* Select *GNU General Public Licence v3.0* to be inline with *db4e*'s licensing.
* Click on the *Create repository* button.

---

# Setup GitHub Pages

You need to configure the repository as a *GitHub Pages* site. Once you've created your repository...

* Click on the *Settings* gear, near the top-right corner of the repository screen.
* Under the *Code and Automation* section, select *Pages*.
* Change the *Branch* from *None* to *main* and click the *Save* button.
* Optionally put in a custom domain (e.g. *xmr.osoyalce.com*). **NOTE:** You will need to be able to create DNS records in the domain for this to work.

---

# Generate a SSH Key

SSH keys are used to authenticate to GitHub. This is so you can upload report data to your website. Login to *GitHub*. The SSH key that's needed is the one associated with the user who will be running the *db4e* application (e.g. *sally*, or *db4e*). The account's public key is in the user's home directory:

Check if you already have a SSH key:

```
ls -l ~/.ssh/id_rsa.pub 
```

If you do not already have an ssh-key you can easily generate one with the `ssh-keygen` command:

```
ssh-keygen -b 10240
```

When prompted:

```
Enter file in which to save the key (/home/sally/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
```

-simply hit enter (default path, empty passphrase).

---

# Import Key into GitHub

Next you'll want to import the **public** part of your new key to GitHub. This file is `~/.ssh/id_rsa.pub`.

* Once you've logged into *GitHub*, click on your account icon in the top-right corner to access the drop down menu. 
* Click on *Settings* (not the repository settings).
* Click on *SSH and GPG keys*.
* Click on the *New SSH key* button.
* Enter a name for the key, e.g. *db4e on my_server*.
* Next you'll want to cut-and-paste the contents of the public key file (~/.ssh/id_rsa.pub) into the *Key* box in GitHub.

---

# Setup the db4e Service

See the [Setup the db4e Service](/pages/Setup-db4e-Service.html) for information on setting up the *db4e* service.

---

# Hashrate Reports

The pool, sidechain and mainchain hashrate reports aren't automatically generated by *db4e*. Instead you'll need to 
setup a cronjob (`crontab -e` command) to run these reports periodically. Here's an example crontab entry:

```
# Generate a hashrates report every hour
0 * * * * /opt/prod/db4e/bin/db4e.sh -r hashrates
```

**IMPORTANT NOTE**: The cronjob should be installed using the same Linux account name that you are using to run the *db4e* application. This account name is referenced in the *systemd* service definition file (see [Setup the db4e Service](/pages/Setup-db4e-Service.html)) and is also the owner of the *db4e* files and the *website repo* files.

---

# MongoDB Backups

A comprehensive backup of MongoDb has been implemented by running `db4e.sh -b`. The code will backup the MongoDB databases into your local *GitHub Pages website* in the `backups` directory. Currently the script keeps 7 backups before rotating them out. The implementation also pushes the backups to GitHub so you have off-site storage for free!

**PRO-TIP**: Create a cronjob to schedule daily backups. E.g.

```
# Do a daily DB backup at noon
0 12 * * * /opt/prod/db4e/bin/db4e.sh -b
```







