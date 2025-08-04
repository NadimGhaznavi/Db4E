#!/bin/bash
#
# <vendor-dir>/p2pool-<version>/bin/start-p2pool.sh
#
# /etc/systemd/system/db4e.service
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi 
#    Copyright: (c) 2024-2025 NadimGhaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0
#
# Start script for P2Pool
#
#####################################################################


# Get the deployment specific settings
INI_FILE=$1
if [ -z $INI_FILE ]; then
	echo "Usage: $0 <INI FIle>"
	exit 1
fi

source $INI_FILE

if [ "$CHAIN" == 'mainchain' ]; then
	CHAIN_OPTION=''
elif [ "$CHAIN" == 'minisidechain' ]; then
	CHAIN_OPTION='--mini'
elif [ "$CHAIN" == 'nanosidechain' ]; then
	CHAIN_OPTION='--nano'
else
	echo "ERROR: Invalid chain ($CHAIN), valid options are 'mainchain', 'minisidechain' or 'nanosidechain'"
	exit 1
fi

# The values are in the p2pool.ini file
STDIN=${RUN_DIR}/p2pool.stdin
P2POOL="${P2P_DIR}/bin/p2pool"

$P2POOL \
	--host ${MONERO_NODE} \
	--wallet ${WALLET} \
	--no-color \
	--stratum ${ANY_IP}:${STRATUM_PORT} \
	--p2p ${ANY_IP}:${P2P_PORT} \
	--rpc-port ${RPC_PORT} \
	--zmq-port ${ZMQ_PORT} \
	--loglevel ${LOG_LEVEL} \
	--data-dir ${LOG_DIR} \
	--in-peers ${IN_PEERS} \
	--out-peers ${OUT_PEERS} \
	--data-api ${API_DIR} ${CHAIN_OPTION}
