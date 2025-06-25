#!/bin/bash
#
# Start script for P2Pool
#
#####################################################################


#####################################################################
#
#  This file is part of *db4e*, the *Database 4 Everything* project
#  <https://github.com/NadimGhaznavi/db4e>, developed independently
#  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
#  <https://github.com/NadimGhaznavi/db4e>.
# 
#  This program is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as 
#  published by the Free Software Foundation, version 3.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy (LICENSE.txt) of the GNU General 
#  Public License along with this program. If not, see 
#  <http://www.gnu.org/licenses/>.
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
