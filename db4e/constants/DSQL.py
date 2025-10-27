"""
db4e/constants/DSQL.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

# Utility class
from db4e.util.ConstGroup import ConstGroup


class DTable(ConstGroup):

    # Deployment record tables
    DB4E: str = "db4e"
    MONEROD: str = "monerod"
    MONEROD_REMOTE: str = "monerod_remote"
    P2POOL: str = "p2pool"
    P2POOL_REMOTE: str = "p2pool_remote"
    P2POOL_INTERNAL: str = "p2pool_internal"
    XMRIG: str = "xmrig"
    XMRIG_REMOTE: str = "xmrig_remote"

    # Operations record tables
    CURRENT_UPTIME: str = "current_uptime"
    TOTAL_UPTIME: str = "total_uptime"
    TUI_LOG_LINE: str = "tui_log_line"

    # Mining record tables
    BLOCK_FOUND_EVENT: str = "block_found_event"
    CHAIN_HASHRATE: str = "chain_hashrate"
    CHAIN_MINERS: str = "chain_miners"
    MINER_HASHRATE: str = "miner_hashrate"
    POOL_HASHRATE: str = "pool_hashrate"
    SHARE_FOUND_EVENT: str = "share_found_event"
    SHARE_POSITION: str = "share_position"
    XMR_PAYMENT: str = "xmr_payment"


class DCol(ConstGroup):
    ANY_IP: str = "any_ip"
    BLOCKCHAIN_DIR: str = "blockchain_dir"
    CHAIN: str = "chain"
    CONFIG_FILE: str = "config_file"
    DETAILS: str = "details"
    DONATION_WALLET: str = "donation_wallet"
    DB4E_GROUP: str = "db4e_group"
    DB4E_USER: str = "db4e_user"
    EFFORT: str = "effort"
    ELEMENT: str = "element"
    ELEMENT_TYPE: str = "element_type"
    ENABLED: str = "enabled"
    EVENT: str = "event"
    HASHRATE: str = "hashrate"
    ID: str = "id"
    IN_PEERS: str = "in_peers"
    INSTALL_DIR: str = "install_dir"
    INSTANCE: str = "instance"
    IP_ADDR: str = "ip_addr"
    LOG_LEVEL: str = "log_level"
    LOG_FILE: str = "log_file"
    LOGROTATE_CONFIG: str = "logrotate_config"
    MAX_LOG_FILES: str = "max_log_files"
    MAX_LOG_SIZE: str = "max_log_size"
    MESSAGE: str = "message"
    MINER: str = "miner"
    MINERS: str = "miners"
    OPERATION: str = "operation"
    OUT_PEERS: str = "out_peers"
    P2P_BIND_PORT: str = "p2p_bind_port"
    P2P_PORT: str = "p2p_port"
    PARENT: str = "parent"
    PICONERO: str = "piconero"
    POOL: str = "pool"
    PRIMARY_SERVER: str = "primary_server"
    PRIORITY_NODE_1: str = "priority_node_1"
    PRIORITY_PORT_1: str = "priority_port_1"
    PRIORITY_NODE_2: str = "priority_node_2"
    PRIORITY_PORT_2: str = "priority_port_2"
    RPC_BIND_PORT: str = "rpc_bind_port"
    SHARE_POSITION: str = "share_position"
    SHOW_TIME_STATS: str = "show_time_stats"
    START_TIME: str = "start_time"
    STATUS: str = "status"
    STDIN_PATH: str = "stdin_path"
    STOP_TIME: str = "stop_time"
    STRATUM_PORT: str = "stratum_port"
    TRACKED_INSTANCE: str = "tracked_instance"
    TRACKED_TYPE: str = "tracked_type"
    UPDATED_YEAR: str = "updated_y"
    UPDATED_MONTH: str = "updated_mo"
    UPDATED_DAY: str = "updated_d"
    UPDATED_HOUR: str = "updated_h"
    UPDATED_MINUTE: str = "updated_mi"
    UPDATED_SECOND: str = "updated_s"
    UPTIME_SECS: str = "uptime_secs"
    USER_WALLET: str = "user_wallet"
    VENDOR_DIR: str = "vendor_dir"
    VERSION: str = "version"
    ZMQ_PUB_PORT: str = "zmq_pub_port"
    ZMQ_RPC_PORT: str = "zmq_rpc_port"


ELEM_TABLE_LIST = [
    DTable.DB4E,
    DTable.MONEROD,
    DTable.MONEROD_REMOTE,
    DTable.P2POOL,
    DTable.P2POOL_REMOTE,
    DTable.P2POOL_INTERNAL,
    DTable.XMRIG,
    DTable.XMRIG_REMOTE,
]

MINING_TABLE_LIST = [
    DTable.BLOCK_FOUND_EVENT,
    DTable.CHAIN_HASHRATE,
    DTable.CHAIN_MINERS,
    DTable.MINER_HASHRATE,
    DTable.POOL_HASHRATE,
    DTable.SHARE_FOUND_EVENT,
    DTable.SHARE_POSITION,
    DTable.XMR_PAYMENT,
]

OPS_TABLE_LIST = [
    DTable.CURRENT_UPTIME,
    DTable.TOTAL_UPTIME,
    DTable.TUI_LOG_LINE,
]
