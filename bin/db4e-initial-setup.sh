#!/bin/bash
#
# bin/db4e-initial-setup.sh
#
# This script does the initial db4e setup. It is run using sudo
# The *db4e* application does NOT keep or store the root password.
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

DB4E_DIR="$1"
DB4E_USER="$2"
DB4E_GROUP="$3"
VENDOR_DIR="$4"

if [ -z "$VENDOR_DIR" ]; then
    echo "Usage: $0 <db4e_directory> <db4e_user> <db4e_group> <vendor_dir>"
    exit 1
fi

# Create the db4e (system) group
groupadd -r $DB4E_GROUP
echo "Created the db4e group: $DB4E_GROUP"

# Create the db4e user
usermod -a -G $DB4E_GROUP $DB4E_USER
echo "Added user ($DB4E_USER) to the new group ($DB4E_GROUP)"

# Update the sudoers file
TMP_SUDOERS=/tmp/sudoers
cp /etc/sudoers $TMP_SUDOERS
echo "# Grant the db4e user permission to start and stop db4d, P2Pool and monerod" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl start db4e" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop db4e" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable db4e" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl start p2pool@*" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop p2pool@*" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable p2pool@*" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl start monerod@*" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop monerod@*" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable monerod@*" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl start xmrig@*" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop xmrig@*" >> $TMP_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable xmrig@*" >> $TMP_SUDOERS
visudo -c -f $TMP_SUDOERS > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Invalid sudoers file, aborting"
    rm $TMP_SUDOERS
    exit 1
fi
cp /etc/sudoers /etc/sudoers.db4e
mv /tmp/sudoers /etc/sudoers
echo "Updated /etc/sudoers, original is backed up as /etc/sudoers.db4e"

# Install the db4e, P2Pool and Monerod systemd files
TMP_DIR=/tmp/db4e
mv $TMP_DIR/db4e.service /etc/systemd/system
echo "Installed the db4e systemd service"
mv $TMP_DIR/p2pool@.service /etc/systemd/system
mv $TMP_DIR/p2pool@.socket /etc/systemd/system
echo "Installed the P2Pool systemd service"
mv $TMP_DIR/monerod@.service /etc/systemd/system
mv $TMP_DIR/monerod@.socket /etc/systemd/system
echo "Installed the Monero daemon systemd service"
mv $TMP_DIR/xmrig@.service /etc/systemd/system
echo "Installed the XMRig miner systemd service"

systemctl daemon-reload
echo "Reloaded the systemd configuration"
systemctl enable db4e
echo "Configured the db4e service to start at boot time"
systemctl start db4e
echo "Started the db4e service"

# Set SUID bit on the xmrig binary for performance reasons
chown root:$DB4E_GROUP $VENDOR_DIR/xmrig-*/bin/xmrig
chmod 4750 $VENDOR_DIR/xmrig-*/bin/xmrig
echo "Set the SUID bit on the xmrig binary"
