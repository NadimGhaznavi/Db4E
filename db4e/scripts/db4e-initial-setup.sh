#!/bin/bash

# db4e/bin/db4e-initial-setup.sh

#   Database 4 Everything
#   Author: Nadim-Daniel Ghaznavi 
#   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#   License: GPL 3.0

DB4E_DIR="$1"
DB4E_USER="$2"
DB4E_GROUP="$3"
VENDOR_DIR="$4"

if [ -z "$VENDOR_DIR" ]; then
    echo "Usage: $0 <db4e_directory> <db4e_user> <db4e_group> <vendor_dir>"
    exit 1
fi

# Delete the old group if this env var was set
if [ ! -z "$DB4E_OLD_GROUP" ]; then
    groupdel "$DB4E_OLD_GROUP"
    echo "Deleted old group ($DB4E_OLD_GROUP)"
fi

# Create the db4e (system) group
groupadd -r $DB4E_GROUP
echo "Created the db4e group: $DB4E_GROUP"

# Create the db4e user
usermod -a -G $DB4E_GROUP $DB4E_USER
echo "Added user ($DB4E_USER) to the new group ($DB4E_GROUP)"

# Update the sudoers file
DB4E_SUDOERS="/etc/sudoers.d/db4e"
echo "# Grant the db4e user permission to start and stop db4d, P2Pool and monerod" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl start db4e" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop db4e" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable db4e" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl start p2pool@*" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop p2pool@*" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable p2pool@*" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl start monerod@*" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop monerod@*" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable monerod@*" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl start xmrig@*" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl stop xmrig@*" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /bin/systemctl enable xmrig@*" >> $DB4E_SUDOERS
chgrp sudo "$SUDOERS_DROPIN"
chmod 440 "$SUDOERS_DROPIN"

visudo -c -f $DB4E_SUDOERS > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Invalid sudoers file ($DB4E_SUDOERS), aborting"
    rm $DB4E_SUDOERS
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
chown root:"$DB4E_GROUP" "$VENDOR_DIR/xmrig-*/bin/xmrig"
chmod 4750 "$VENDOR_DIR/xmrig-*/bin/xmrig"
echo "Set the SUID bit on the xmrig binary"
