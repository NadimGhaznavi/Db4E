
---
title: "Pre-Requisites for db4e Installation"
date: 2025-06-01
markdown: GFM
category:
  - db4e
tags:
  - installation
---

# MongoDB

See [Installing MongoDB on Debian Linux](/pages/ops/Installing-MongoDB.html).

# Support for db4e-os.py 

The db4e-os.py program relies on additional standard Python libraries. These must be installed in a sandboxed Python environment for enhanced security.

## Python3 Sandbox Support

This is to provide support for installing a sandboxed version of Python which is used to run the application. This allows for the installation of additional Python libraries without polluting the host system.

```
apt install python3.11-venv
apt install python3-pip
cd /opt/prod/db4e
python3 -m venv db4e_python
```

## Installing additional Python Libraries
```
. /opt/prod/db4e/db4e_python/bin/activate
pip install install pygame
```



