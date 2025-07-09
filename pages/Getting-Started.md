---
title: Getting Started
---

# 📜 Introduction

This guide will walk you through setting up **Database 4 Everything (Db4E)** on your system, from installing dependencies to launching the application.

---

# 📝 Prerequisites

## ✅ Debian Linux

Db4E is certified for [Debian 12 “Bookworm”](https://debian.org) and works best on a clean, minimal installation.  
We recommend the [NetInst ISO](https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.11.0-amd64-netinst.iso) with only the following option selected during setup:

- Standard system utilities

Db4E should also run on other modern Linux distributions with minimal changes.

---

## 📥 Required Packages

Before installing Db4E, make sure the following packages are installed:

```bash
sudo apt-get install gnupg curl libhwloc15 python3.11-venv libzmq5 pip
```

### 📦 Why they're needed

* `gnupg`, `curl` — for installing MongoDB
* `libhwloc15` — required by XMRig
* `python3.11-venv`, `pip` — for Python virtual environment and installing Db4E
* `libzmq5` — required by P2Pool

---

## 🕵️ Dedicated db4e Account (Optional)

**Pro Tip**: For security and isolation, we recommend creating a dedicated Linux user for Db4E (e.g., `db4e`). This step is optional, but considered a best practice.

---

# 🗃️ Install MongoDB

MongoDB is not included in Debian’s default repositories.
See the [Installing MongoDB](/pages/Installing-MongoDB.html) page for full instructions on setting up the official MongoDB Community Edition repository and installing the database.

---

# 🔧 Set Up a Python Virtual Environment

Db4E is distributed as a [PyPI package](https://pypi.org/project/db4e/). It's recommended to install it inside a virtual environment:

```bash
python3 -m venv db4e
. db4e/bin/activate
```

---

# ✅ Install Db4E

Once your virtual environment is activated:

```bash
pip install db4e
```

---

# 🧩 Initial Install & Setup

Launch Db4E from your virtual environment:

```bash
db4e
```

On first launch, you’ll be guided through the Initial Install screen.

You’ll be asked to provide:

* Your Monero wallet address (for mining payouts)
* A **deployment directory** (used to store binaries, configuration files, logs etc.)

Once you click **Proceed**, Db4E will perform an environment setup using elevated privileges via `sudo`.


## ⚙️ What the Installer Does

The `db4e-initial-setup.sh` script performs the following:

* Creates a custom sudoers entry (`/etc/sudoers.d/db4e`) to allow system control of Monero, P2Pool, and XMRig without prompting for a password
* Installs systemd service definitions for all Db4E-managed components under `/etc/systemd/system/`
* Sets XMRig ownership to `root` and sets the `suid` bit so it can access CPU MSRs (model-specific registers) for optimized performance

---

# 🔐 Sudo Configuration (Temporary)

For the Initial Install to complete successfully, your user must be able to execute `sudo` commands without being prompted for a password.

If you’re using the default Debian sudo configuration:

```bash
%sudo    ALL=(ALL:ALL) ALL
```

You must temporarily change it to:

```bash
%sudo    ALL=(ALL:ALL) NOPASSWD: ALL
```

⚠️ **Important**: After completing the Initial Install, you can safely revert this change.

---

# 🚀 Launch Db4E

To launch the application from your virtual environment:

```bash
db4e
```

Db4E will start in terminal UI (TUI) mode. If setup was successful, you’ll see the main dashboard interface.

---

# 🚧 What’s Next

The current release sets up the core environment and provides a functional TUI interface.

Coming soon:

- Remote and local Monero daemon configuration
- P2Pool and XMRig deployment management
- Performance monitoring and system health checks

Stay tuned — these features are actively in development.  
In the meantime, you can follow updates on the [Blog](https://blog.osoyalce.com/) or join the discussion on [GitHub Discussions](https://github.com/NadimGhaznavi/db4e/discussions).
