#!/bin/bash
#
# <vendor-dir>/p2pool/bin/start-p2pool.sh
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

STRATUM_BAN_TIME=120 # Seconds, default is 600

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
	--wallet ${WALLET} \
	--host ${MONERO_NODE} \
	--rpc-port ${RPC_PORT} \
	--zmq-port ${ZMQ_PUB_PORT} \
	--stratum ${ANY_IP}:${STRATUM_PORT} \
	--p2p ${ANY_IP}:${P2P_PORT} \
	--stratum-ban-time ${STRATUM_BAN_TIME} \
	--loglevel ${LOG_LEVEL} \
	--data-dir ${LOG_DIR} \
	--data-api ${API_DIR} \
	--local-api \
	--no-color \
	--out-peers ${OUT_PEERS} \
	--in-peers ${IN_PEERS} \
	${CHAIN_OPTION}
