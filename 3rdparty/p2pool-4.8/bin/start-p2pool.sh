#!/bin/bash

# Get the deployment specific settings
INI_FILE=$1

source $INI_FILE

# The values are in the p2pool.ini file
STDIN=${RUN_DIR}/p2pool.stdin
DATA_API_DIR="${P2P_DIR}/api"
P2P_LOG="${LOG_DIR}/p2pool.log"
P2POOL="${P2P_DIR}/bin/p2pool"

# Create the API directory if it doesn't already exist
if [ ! -d $API_DIR ]; then
  mkdir ${API_DIR}
fi

# Create the run directory if it doesn't already exist
if [ ! -d ${RUN_DIR} ]; then
	mkdir -p ${RUN_DIR}
fi

# Create the logs directory if it doesn't already exist
if [ ! -d ${LOG_DIR} ]; then
	mkdir -p ${LOG_DIR}
fi

$P2POOL \
	--host ${MONERO_NODE} \
	--wallet ${WALLET} \
	--mini \
	--no-color \
	--stratum ${ANY_IP}:${STRATUM_PORT} \
	--p2p ${ANY_IP}:${P2P_PORT} \
	--rpc-port ${RPC_PORT} \
	--zmq-port ${ZMQ_PORT} \
	--loglevel ${LOG_LEVEL} \
	--data-dir ${LOG_DIR} \
	--in-peers ${IN_PEERS} \
	--out-peers ${OUT_PEERS} \
	--data-api ${API_DIR}
