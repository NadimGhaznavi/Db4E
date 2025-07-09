#!/bin/bash
#
# db4e/bin/db4e-initial-setup.sh
#
# Initial setup script. Run by the InstallMgr with sudo.
#
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi 
#    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#    License: GPL 3.0
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

# Update the sudoers file
DB4E_SUDOERS="/etc/sudoers.d/db4e"
echo "# Grant the db4e user permission to start and stop db4d, P2Pool and monerod" > $DB4E_SUDOERS
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

# Validae the 
visudo -c -f $DB4E_SUDOERS > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Invalid sudoers file ($DB4E_SUDOERS), aborting"
    rm $DB4E_SUDOERS
    exit 1
fi
echo "Created custom sudo file ($DB4E_SUDOERS)"

TMP_DIR=$DB4E_TMP_DIR
SYSTEMD_DIR=/etc/systemd/system

# Install the Db4E service definition file
mv $TMP_DIR/db4e.service $SYSTEMD_DIR
chown root:root $SYSTEMD_DIR/db4e.service
chmod 0644 $SYSTEMD_DIR/db4e.service
echo "Installed the db4e systemd service"

# Install the Monero daemon service definition file
mv $TMP_DIR/monerod@.service $SYSTEMD_DIR
mv $TMP_DIR/monerod@.socket $SYSTEMD_DIR
chown root:root $SYSTEMD_DIR/monerod@.service
chown root:root $SYSTEMD_DIR/monerod@.socket
chmod 0644 $SYSTEMD_DIR/monerod@.service
chmod 0644 $SYSTEMD_DIR/monerod@.socket
echo "Installed the Monero daemon systemd service"

# Install the P2Pool service definition file
mv $TMP_DIR/p2pool@.service $SYSTEMD_DIR
mv $TMP_DIR/p2pool@.socket $SYSTEMD_DIR
chown root:root $SYSTEMD_DIR/p2pool@.service
chown root:root $SYSTEMD_DIR/p2pool@.socket
chmod 0644 $SYSTEMD_DIR/p2pool@.service
chmod 0644 $SYSTEMD_DIR/p2pool@.socket
echo "Installed the P2Pool systemd service"

# Install the XMRig service definition file
mv $TMP_DIR/xmrig@.service $SYSTEMD_DIR
chown root:root $SYSTEMD_DIR/xmrig@.service
chmod 0644 $SYSTEMD_DIR/xmrig@.service
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
