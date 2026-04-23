#!/bin/bash

MON_DIR=/opt/Db4E/monerod/Islands/blockchain

if [ ! -d $MON_DIR ]; then
  echo "ERROR: Missing local MoneroD deployment: $MON_DIR"
  exit 1
fi

sudo rm -rf $MON_DIR
sudo mkdir $MON_DIR
sudo ln -s /opt/prod/monero-blockchain/lmdb $MON_DIR/lmdb


