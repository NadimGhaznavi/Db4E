"""
db4e/Constants/DPlaceholder.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Used to generate the systemd service definition files in the InstallMgr using
service definition templates.
"""

from db4e.Modules.ConstGroup import ConstGroup

class DPlaceholder(ConstGroup):
    ANY_IP : str = "ANY_IP"
    API_DIR : str = "API_DIR"
    BLOCKCHAIN_DIR : str = "BLOCKCHAIN_DIR"
    CHAIN : str = "CHAIN"
    DB4E_USER : str = "DB4E_USER"
    DB4E_GROUP : str = "DB4E_GROUP"
    DB4E_DIR : str = "DB4E_DIR"
    INSTALL_DIR : str = "INSTALL_DIR"
    INSTANCE : str = "INSTANCE"
    IN_PEERS : str = "IN_PEERS"
    LOG_DIR : str = "LOG_DIR"
    LOG_FILE : str = "LOG_FILE"
    LOG_LEVEL : str = "LOG_LEVEL"
    MAX_LOG_FILES : str = "MAX_LOG_FILES"
    MAX_LOG_SIZE : str = "MAX_LOG_SIZE"
    MINER_NAME : str = "MINER_NAME"
    MONEROD_DIR : str = "MONEROD_DIR"
    MONEROD_IP : str = "MONEROD_IP"
    NUM_THREADS : str = "NUM_THREADS"
    P2P_DIR : str = "P2P_DIR"
    P2POOL_DIR : str = "P2POOL_DIR"
    OUT_PEERS : str = "OUT_PEERS"
    P2P_PORT : str = "P2P_PORT"
    P2P_BIND_PORT : str = "P2P_BIND_PORT"
    PRIORITY_NODE_1 : str = "PRIORITY_NODE_1"
    PRIORITY_PORT_1 : str = "PRIORITY_PORT_1"
    PRIORITY_NODE_2 : str = "PRIORITY_NODE_2"
    PRIORITY_PORT_2 : str = "PRIORITY_PORT_2"
    RPC_BIND_PORT : str = "RPC_BIND_PORT"
    RUN_DIR : str = "RUN_DIR"
    SHOW_TIME_STATS : str = "SHOW_TIME_STATS"
    STDIN_PATH : str = "STDIN_PATH"
    STRATUM_PORT : str = "STRATUM_PORT"
    PYTHON : str = "PYTHON"
    URL : str = "URL"
    WALLET : str = "WALLET"
    XMRIG_DIR : str = "XMRIG_DIR"
    ZMQ_PUB_PORT : str = "ZMQ_PUB_PORT"
    ZMQ_RPC_PORT : str = "ZMQ_RPC_PORT"
