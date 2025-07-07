#!/bin/bash
#
# bin/db4e-install-service.sh
#
# This script installs the db4e service. It exists for the scenario
# where the db4e service was uninstalled for whatever reason.
#
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi 
#    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#    License: GPL 3.0
#
#####################################################################

# Install the db4e service, called from the Db4eOSTui class
TMP_DIR=/tmp/db4e
mv $TMP_DIR/db4e.service /etc/systemd/system
echo "Installed the db4e systemd service"

systemctl daemon-reload
echo "Reloaded the systemd configuration"
systemctl enable db4e
echo "Configured the db4e service to start at boot time"
systemctl start db4e
echo "Started the db4e service"
