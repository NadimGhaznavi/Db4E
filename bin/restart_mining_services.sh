#!/bin/bash -x

systemctl stop monerod
sleep 1
systemctl start monerod
sleep 1
systemctl stop p2pool
sleep 1
rm -f /opt/prod/p2pool/p2pool.cache
systemctl start p2pool
sleep 120
systemctl stop db4e_monitor_p2pool_log
sleep 1
systemctl start db4e_monitor_p2pool_log

