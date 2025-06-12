#!/bin/bash
#
# This script installs the *db4e* service and configures it to 
# start when your system boots. This script is run by db4e
# with using sudo. The *db4e* application does NOT keep or 
# store your root user password.
#
#####################################################################


#####################################################################
#
#  This file is part of *db4e*, the *Database 4 Everything* project
#  <https://github.com/NadimGhaznavi/db4e>, developed independently
#  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
#  <https://github.com/NadimGhaznavi/db4e>.
# 
#  This program is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as 
#  published by the Free Software Foundation, version 3.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy (LICENSE.txt) of the GNU General 
#  Public License along with this program. If not, see 
#  <http://www.gnu.org/licenses/>.
#
#####################################################################

SERVICE_SRC="$1"  
SERVICE_DEST="/etc/systemd/system/db4e.service"

if [ -z "$SERVICE_SRC" ]; then
    echo "Usage: $0 /path/to/generated/service/file"
    exit 1
fi

if [ ! -f "$SERVICE_SRC" ]; then
    echo "Service file not found: $SERVICE_SRC"
    exit 2
fi

cp "$SERVICE_SRC" "$SERVICE_DEST"
echo "Copied $SERVICE_SRC to $SERVICE_DEST"

# Reload systemd, enable and start the service
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"
echo "$SERVICE_NAME installed and started."
