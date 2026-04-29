#!/bin/bash
#

DB4E_SRC=/opt/dev/db4e
DB4E_DEST=/home/sally/db4e

echo -n "Stopping db4e service: "
sudo systemctl stop db4e > /dev/null 2>&1
echo "DONE"


echo -n "Deleting custom /etc/sudoers.d/db4e: "
sudo rm /etc/sudoers.d/db4e  2> /dev/null
echo "DONE"

echo -n "Deleting systemd services: "
SYSTEMD=/etc/systemd/system
sudo rm $SYSTEMD/db4e.service 2> /dev/null
sudo rm $SYSTEMD/monerod@.service 2> /dev/null
sudo rm $SYSTEMD/monerod@.socket 2> /dev/null
sudo rm $SYSTEMD/p2pool@.service 2> /dev/null
sudo rm $SYSTEMD/p2pool@.socket 2> /dev/null
sudo rm $SYSTEMD/xmrig@.service 2> /dev/null
sudo systemctl daemon-reload
echo "DONE"

echo -n "Deleting /opt/Db4E (and backups): "
sudo rm -rf /opt/Db4E**
echo "DONE"

echo -n "Deleting the ~/.db4e bootstrap file: "
rm -rf "~/.db4e"
echo "DONE"
