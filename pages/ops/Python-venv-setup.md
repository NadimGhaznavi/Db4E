---
title: "Python venv Setup"
---

# Introduction

This page provides detailed information on how the Python venv environment was constructed.

# Initial Setup

The venv environment was created within the *db4e* install directory (e.g. `/opt/prod/db4e`):

```
cd /opt/prod/db4e
python3 -m venv venv
```

# Pip Packages

Additional packages were added using Pip:

```
. /opt/prod/db4e/venv/bin/activate
(venv) pip install pymongo
(venv) pip install pyyaml
(venv) pip install requests
(vent) pip install urwid
```

