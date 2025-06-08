---
title: "Building P2Pool from Source"
---

Directory
Source code | `/opt/src`
Build directory | `/opt/build`
Installed software | `/opt/prod`

Directory               | Description
------------------------|-------------------
`/opt/src/p2pool-v4.6`  | Source code
`/opt/prod/p2pool-v4.6` | Installed code
`/opt/prod/p2pool`      | Symlink to installed code directory

Within the installed software directories I use the following convention:

Directory   | Description
------------|-------------------
`bin`       | Directory to house executibles 
`logs`      | Directory to house logs
`conf`      | Directory to house configuration files
`run`       | Directory to contain temporary runtime files
