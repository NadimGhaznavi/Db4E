#!/bin/bash
#
# bin/db4e-install-service.sh
#
# This script installs the db4e service. It exists for the scenario
# where the db4e service was uninstalled for whatever reason.
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
