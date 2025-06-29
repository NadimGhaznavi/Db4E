#!/bin/bash
#
# bin/db4e-uninstall-service.sh
#
# This script removes the *db4e* service. This script is run by db4e
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
 
SERVICE_FILE="/etc/systemd/system/db4e.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo "Service file not found: $SERVICE_FILE"
    exit 2
fi

rm -f $SERVICE_FILE

# Reload systemd, enable and start the service
systemctl daemon-reexec
systemctl daemon-reload
echo "The db4e service has been removed from your system."
echo
echo "* Removed systemd service definition: $SERVICE_FILE"
echo "* Reloaded systemd's configuration"
