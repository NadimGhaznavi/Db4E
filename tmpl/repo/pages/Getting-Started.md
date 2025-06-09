---
title: Getting Started
---

# Introduction

This page will guide you through the process of setting up the *Database 4 Everything* on your system.

---

# Pre-Requisites

---

## Debian Linux

While *db4e* is certified for [Debian](https://debian.org) [12 Bookworm](https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.11.0-amd64-netinst.iso) Linux, it should work with minimal tweaks on any Linux distribution.

This guide assumes a *minimal* (NetInst) install with only:

  * SSH server
  * Standard system utilities* 

-selected.

---

## Root Access

The *db4e* application does *NOT* require root access to run. However, root access is required to:

* Install Pre-Requisite Linux packages
* Install MongoDB
* Run the XMRig miner 
* Configure sudo for XMRig control
* Configure *db4e* as a system service

---

## Dedicated db4e Account

**PRO TIP:** The *best practise* is to created a dedicated Linux *db4e* account and have that account own the *db4e* code and the *GitHub Pages* repository. This is optional.

---

## Create a GitHub Account

If you don't already have one, you can get a free GitHub account.

* Navigate to [https://github.com](https://github.com) and click on the *Sign up* button.

![GitHub Signup](/images/github_sign_up.png)

---

## Create a GitHub Repository

Next you'll need to create a GitHub repository.

* Navigate to [https://github.com](https://github.com) and click on the *Sign in* button.

![GitHub Signup](/images/github_sign_in.png)

* Once you've signed in, click on the 