#!/bin/bash
#
# bin/db4e-uninstall-service.sh
#
# This script removes the *db4e* service. This script is run by db4e
# with using sudo. The *db4e* application does NOT keep or 
# store your root user password.
#
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi 
#    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#    License: GPL 3.0
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
