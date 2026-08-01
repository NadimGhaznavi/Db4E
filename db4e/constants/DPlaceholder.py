# db4e/Constants/DPlaceholder.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0
#
# Used to generate the systemd service definition files in the InstallMgr using
# service definition templates.


from typing import Final


class DPlaceholder:
    ANY_IP: Final[str] = "ANY_IP"
    API_DIR: Final[str] = "API_DIR"
    BLOCKCHAIN_DIR: Final[str] = "BLOCKCHAIN_DIR"
    CHAIN: Final[str] = "CHAIN"
    DB4E_USER: Final[str] = "DB4E_USER"
    DB4E_GROUP: Final[str] = "DB4E_GROUP"
    DB4E_DIR: Final[str] = "DB4E_DIR"
    HTTP_PORT: Final[str] = "HTTP_PORT"
    INSTALL_DIR: Final[str] = "INSTALL_DIR"
    INSTANCE: Final[str] = "INSTANCE"
    IN_PEERS: Final[str] = "IN_PEERS"
    LOG_DIR: Final[str] = "LOG_DIR"
    LOG_FILE: Final[str] = "LOG_FILE"
    LOG_LEVEL: Final[str] = "LOG_LEVEL"
    MAX_LOG_FILES: Final[str] = "MAX_LOG_FILES"
    MAX_LOG_SIZE: Final[str] = "MAX_LOG_SIZE"
    MINER_NAME: Final[str] = "MINER_NAME"
    MONEROD_DIR: Final[str] = "MONEROD_DIR"
    MONEROD_IP: Final[str] = "MONEROD_IP"
    NUM_THREADS: Final[str] = "NUM_THREADS"
    P2P_DIR: Final[str] = "P2P_DIR"
    P2POOL_DIR: Final[str] = "P2POOL_DIR"
    OUT_PEERS: Final[str] = "OUT_PEERS"
    P2P_PORT: Final[str] = "P2P_PORT"
    P2P_BIND_PORT: Final[str] = "P2P_BIND_PORT"
    PRIORITY_NODE_1: Final[str] = "PRIORITY_NODE_1"
    PRIORITY_PORT_1: Final[str] = "PRIORITY_PORT_1"
    PRIORITY_NODE_2: Final[str] = "PRIORITY_NODE_2"
    PRIORITY_PORT_2: Final[str] = "PRIORITY_PORT_2"
    RPC_BIND_PORT: Final[str] = "RPC_BIND_PORT"
    RUN_DIR: Final[str] = "RUN_DIR"
    SHOW_TIME_STATS: Final[str] = "SHOW_TIME_STATS"
    STDIN_PATH: Final[str] = "STDIN_PATH"
    STRATUM_PORT: Final[str] = "STRATUM_PORT"
    PYTHON: Final[str] = "PYTHON"
    URL: Final[str] = "URL"
    VENDOR_DIR: Final[str] = "VENDOR_DIR"
    WALLET: Final[str] = "WALLET"
    XMRIG_DIR: Final[str] = "XMRIG_DIR"
    ZMQ_PUB_PORT: Final[str] = "ZMQ_PUB_PORT"
    ZMQ_RPC_PORT: Final[str] = "ZMQ_RPC_PORT"
