#!/bin/bash
#

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

echo -n "Deleting install dir (and backups): "
sudo rm -rf /opt/Db4E*
echo "DONE"

echo -n "Deleting ~/.db4e: "
rm -rf /home/dan/.db4e
echo "DONE"
