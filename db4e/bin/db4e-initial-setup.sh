#!/bin/bash -x
#
# db4e/bin/db4e-initial-setup.sh
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

DB4E_DIR="$1"
DB4E_USER="$2"
DB4E_GROUP="$3"
VENDOR_DIR="$4"
TMP_DIR="$5"

if [ -z "$TMP_DIR" ]; then
    echo "Usage: $0 <db4e_directory> <db4e_user> <db4e_group> <vendor_dir> <tmp_dir>"
    exit 1
fi

# Update the sudoers file
DB4E_SUDOERS="/etc/sudoers.d/db4e"
echo "# /etc/sudoers.d/db4e" > $DB4E_SUDOERS
echo >> $DB4E_SUDOERS
echo "#" >> $DB4E_SUDOERS
echo "#    Database 4 Everything" >> $DB4E_SUDOERS
echo "#    Author: Nadim-Daniel Ghaznavi" >> $DB4E_SUDOERS
echo "#    Copyright: (c) 2024-2025 NadimGhaznavi" >> $DB4E_SUDOERS
echo "#    GitHub: https://github.com/NadimGhaznavi/db4e" >> $DB4E_SUDOERS
echo "#    License: GPL 3.0" >> $DB4E_SUDOERS
echo "#" >> $DB4E_SUDOERS
echo "#####################################################################" >> $DB4E_SUDOERS
echo >> $DB4E_SUDOERS
echo "# Start and stop Db4E, P2Pool, Monero and XMRig services" >> $DB4E_SUDOERS
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
echo >> $DB4E_SUDOERS
echo "# Run logrotate to manage Db4E, P2Pool and XMRig log files" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /usr/sbin/logrotate $VENDOR_DIR/logrotate" >> $DB4E_SUDOERS
echo "$DB4E_USER ALL=(ALL) NOPASSWD: /usr/bin/chown root $VENDOR_DIR/db4e/logrotate/*" >> $DB4E_SUDOERS

echo >> $DB4E_SUDOERS

chgrp sudo "$DB4E_SUDOERS"
chmod 440 "$DB4E_SUDOERS"

# Validate the sudo config file
visudo -c -f $DB4E_SUDOERS > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Invalid sudoers file ($DB4E_SUDOERS), aborting"
    rm $DB4E_SUDOERS
    exit 1
fi
echo "Installed----$DB4E_SUDOERS"

SYSTEMD_DIR=/etc/systemd/system

# Install the Db4E service definition file
mv $TMP_DIR/db4e.service $SYSTEMD_DIR
if [ $? -ne 0 ]; then
    echo "FATAL ERROR: mv $TMP_DIR/db4e.service $SYSTEMD_DIR failed"
    exit 1
fi
chown root:root $SYSTEMD_DIR/db4e.service
chmod 0644 $SYSTEMD_DIR/db4e.service
echo "Installed----$SYSTEMD_DIR/db4e.service"

# Install the Monero daemon service definition file
mv $TMP_DIR/monerod@.service $SYSTEMD_DIR
mv $TMP_DIR/monerod@.socket $SYSTEMD_DIR
chown root:root $SYSTEMD_DIR/monerod@.service
chown root:root $SYSTEMD_DIR/monerod@.socket
chmod 0644 $SYSTEMD_DIR/monerod@.service
chmod 0644 $SYSTEMD_DIR/monerod@.socket
echo "Installed----$SYSTEMD_DIR/monerod@.service"
echo "Installed----$SYSTEMD_DIR/monerod@.socket)"

# Install the P2Pool service definition file
mv $TMP_DIR/p2pool@.service $SYSTEMD_DIR
mv $TMP_DIR/p2pool@.socket $SYSTEMD_DIR
chown root:root $SYSTEMD_DIR/p2pool@.service
chown root:root $SYSTEMD_DIR/p2pool@.socket
chmod 0644 $SYSTEMD_DIR/p2pool@.service
chmod 0644 $SYSTEMD_DIR/p2pool@.socket
echo "Installed----$SYSTEMD_DIR/p2pool@.service"
echo "Installed----$SYSTEMD_DIR/p2pool@.socket"

# Install the XMRig service definition file
mv $TMP_DIR/xmrig@.service $SYSTEMD_DIR
chown root:root $SYSTEMD_DIR/xmrig@.service
chmod 0644 $SYSTEMD_DIR/xmrig@.service
echo "Installed----$SYSTEMD_DIR/xmrig@.service"

# Ensure a clean environment
# Stop the internal P2Pool sockets
systemctl stop p2pool@Main.socket
systemctl stop p2pool@Mini.socket
systemctl stop p2pool@Nano.socket

systemctl daemon-reload
echo "Run Command----systemctl daemon-reload"
systemctl enable db4e
echo "Run Command----systemctl enable db4e"
systemctl start db4e
echo "Run Command----systemctl start db4e"

# Set SUID bit on the xmrig binary for performance reasons
chown root:"$DB4E_GROUP" "$VENDOR_DIR/xmrig/bin/xmrig"
chmod 4750 "$VENDOR_DIR/xmrig/bin/xmrig"
echo "Set Permissions----$VENDOR_DIR/xmrig/bin/xmrig"

# Set ownership of the installed files
chown -R root:"$DB4E_GROUP" "$VENDOR_DIR"
echo "Set Ownership----$VENDOR_DIR"

