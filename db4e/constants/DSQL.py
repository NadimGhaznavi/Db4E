# db4e/constants/DSQL.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


# Utility class
from typing import Final


class DTable:

    # Deployment record tables
    DB4E: Final[str] = "db4e"
    MONEROD: Final[str] = "monerod"
    MONEROD_REMOTE: Final[str] = "monerod_remote"
    P2POOL: Final[str] = "p2pool"
    P2POOL_REMOTE: Final[str] = "p2pool_remote"
    P2POOL_INTERNAL: Final[str] = "p2pool_internal"
    XMRIG: Final[str] = "xmrig"
    XMRIG_REMOTE: Final[str] = "xmrig_remote"

    # Operations record tables
    CURRENT_UPTIME: Final[str] = "current_uptime"
    TOTAL_UPTIME: Final[str] = "total_uptime"
    TUI_LOG_LINE: Final[str] = "tui_log_line"

    # Mining record tables
    BLOCK_FOUND_EVENT: Final[str] = "block_found_event"
    CHAIN_HASHRATE: Final[str] = "chain_hashrate"
    CHAIN_MINERS: Final[str] = "chain_miners"
    MINER_HASHRATE: Final[str] = "miner_hashrate"
    POOL_HASHRATE: Final[str] = "pool_hashrate"
    SHARE_FOUND_EVENT: Final[str] = "share_found_event"
    SHARE_POSITION: Final[str] = "share_position"
    XMR_PAYMENT: Final[str] = "xmr_payment"

    # Health messages
    HEALTH_STATE: Final[str] = "health_state"


class DCol:
    ANY_IP: Final[str] = "any_ip"
    BLOCKCHAIN_DIR: Final[str] = "blockchain_dir"
    CATEGORY: Final[str] = "category"
    CHAIN: Final[str] = "chain"
    CONFIG_FILE: Final[str] = "config_file"
    CUR_TIME: Final[str] = "cur_time"
    DETAILS: Final[str] = "details"
    DONATION_WALLET: Final[str] = "donation_wallet"
    DB4E_GROUP: Final[str] = "db4e_group"
    DB4E_USER: Final[str] = "db4e_user"
    EFFORT: Final[str] = "effort"
    ELEM_ID: Final[str] = "elem_id"
    ELEMENT: Final[str] = "element"
    ELEMENT_TYPE: Final[str] = "element_type"
    ENABLED: Final[str] = "enabled"
    EVENT: Final[str] = "event"
    HASHRATE: Final[str] = "hashrate"
    ID: Final[str] = "id"
    IN_PEERS: Final[str] = "in_peers"
    INSTALL_DIR: Final[str] = "install_dir"
    INSTANCE: Final[str] = "instance"
    IP_ADDR: Final[str] = "ip_addr"
    LAST_SYNC_TS: Final[str] = "last_sync_ts"
    LOG_LEVEL: Final[str] = "log_level"
    LOG_FILE: Final[str] = "log_file"
    LOGROTATE_CONFIG: Final[str] = "logrotate_config"
    MAX_LOG_FILES: Final[str] = "max_log_files"
    MAX_LOG_SIZE: Final[str] = "max_log_size"
    MESSAGE: Final[str] = "message"
    MINER: Final[str] = "miner"
    MINERS: Final[str] = "miners"
    NEXT_P2P_PORT: Final[str] = "next_p2p_port"
    NEXT_STRATUM_PORT: Final[str] = "next_stratum_port"
    NUM_THREADS: Final[str] = "num_threads"
    OPERATION: Final[str] = "operation"
    OUT_PEERS: Final[str] = "out_peers"
    P2P_BIND_PORT: Final[str] = "p2p_bind_port"
    P2P_PORT: Final[str] = "p2p_port"
    PARENT: Final[str] = "parent"
    PARENT_REMOTE: Final[str] = "parent_remote"
    PICONERO: Final[str] = "piconero"
    POOL: Final[str] = "pool"
    PRIMARY_SERVER: Final[str] = "primary_server"
    PRIMARY_REMOTE: Final[str] = "primary_remote"
    PRIORITY_NODE_1: Final[str] = "priority_node_1"
    PRIORITY_PORT_1: Final[str] = "priority_port_1"
    PRIORITY_NODE_2: Final[str] = "priority_node_2"
    PRIORITY_PORT_2: Final[str] = "priority_port_2"
    RPC_BIND_PORT: Final[str] = "rpc_bind_port"
    SHARE_POSITION: Final[str] = "share_position"
    SHOW_TIME_STATS: Final[str] = "show_time_stats"
    START_TIME: Final[str] = "start_time"
    STATUS: Final[str] = "status"
    STDIN_PATH: Final[str] = "stdin_path"
    STOP_TIME: Final[str] = "stop_time"
    STRATUM_PORT: Final[str] = "stratum_port"
    TRACKED_INSTANCE: Final[str] = "tracked_instance"
    TRACKED_TYPE: Final[str] = "tracked_type"
    UPDATED_YEAR: Final[str] = "updated_y"
    UPDATED_MONTH: Final[str] = "updated_mo"
    UPDATED_DAY: Final[str] = "updated_d"
    UPDATED_HOUR: Final[str] = "updated_h"
    UPDATED_MINUTE: Final[str] = "updated_mi"
    UPDATED_SECOND: Final[str] = "updated_s"
    UPDATED_TS: Final[str] = "updated_ts"
    UPTIME_SECS: Final[str] = "uptime_secs"
    USER_WALLET: Final[str] = "user_wallet"
    VENDOR_DIR: Final[str] = "vendor_dir"
    VERSION: Final[str] = "version"
    ZMQ_PUB_PORT: Final[str] = "zmq_pub_port"
    ZMQ_RPC_PORT: Final[str] = "zmq_rpc_port"


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

HOURLY_MINING_TABLE_LIST = [
    DTable.BLOCK_FOUND_EVENT,
    DTable.CHAIN_HASHRATE,
    DTable.CHAIN_MINERS,
    DTable.MINER_HASHRATE,
    DTable.POOL_HASHRATE,
]

OPS_TABLE_LIST = [
    DTable.CURRENT_UPTIME,
    DTable.TOTAL_UPTIME,
    DTable.TUI_LOG_LINE,
]

HEALTH_STATE_TABLE_LIST = [DTable.HEALTH_STATE]
