#!/bin/bash
#
# bin/db4e-install-service.sh
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
DB4EGROUP="$2"
DB4EUSER="$3"
XMRIG_SRC="$4"
XMRIG_DEST="$5"
SERVICE_DEST="/etc/systemd/system/db4e.service"

# Create the db4e (system) group
groupadd -r $DB4EGROUP

# Add the db4e user to the db4e group
usermod -a -G $DB4EGROUP $DB4EUSER

if [ -z "$XMRIG_DEST" ]; then
    echo "Usage: $0 /path/to/generated/service/file db4e_group db4e_user /path/to/db4e/xmrig /path/to/3rdparty/xmrig"
    exit 1
fi

if [ ! -f "$SERVICE_SRC" ]; then
    echo "Service file not found: $SERVICE_SRC"
    exit 2
fi

# Copy in the xmrig binary and set SUID bit for performance reasons
cp $XMRIG_SRC $XMRIG_DEST
chown root:$DB4EGROUP $XMRIG_DEST
chmod 4750 $XMRIG_DEST

cp $SERVICE_SRC $SERVICE_DEST
# Reload systemd, enable and start the service
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "Created the db4e group: $DB4EGROUP"
echo "Added the db4e user ($DB4EUSER) to the new group"
echo "Created systemd service definition: $SERVICE_DEST"
echo "Set the SUID bit for xmrig ($XMRIG_DEST)"
echo "Reloaded systemd's configuration"
echo "Configured the service to start at boot time"
echo "Started the db4e service"

