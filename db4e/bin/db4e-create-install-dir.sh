#!/bin/bash -x
#
# db4e/bin/db4e-create-install-dir.sh
#
# Initial setup script. Run by the InstallMgr with sudo.
#
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi 
#    Copyright: (c) 2024-2025 NadimGhaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0
#
#####################################################################

TARGET_DIR=/opt/Db4E

DB4E_USER=$1

if [ -e "$TARGET_DIR" ]; then
    echo "Found install dir----/opt/Db4E"
    TS="$(date +%Y%m%d_%H%M%S)"
    mv "$TARGET_DIR" "${TARGET_DIR}.${TS}"
    echo "Backed up----${TARGET_DIR}.${TS}"
fi


mkdir -p "$TARGET_DIR"
chown "$DB4E_USER":root "$TARGET_DIR"
chmod 755 "$TARGET_DIR"
echo "Created directory----${TARGET_DIR}"