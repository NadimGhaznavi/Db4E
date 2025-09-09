"""
db4e/Constants/Fields.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from enum import StrEnum

class DField(StrEnum):
    COMPONENTS = "components"
    CONFIG_FILE = "config_file"
    DATA_DIR = "data_dir"
    DONATION_WALLET = "donation_wallet"
    ELEMENT_TYPE = "element_type"
    FIELD = "field"
    GROUP = "group"
    INSTALL_DIR = "install_dir"
    TEMPLATE = "template"
    TEMPLATES = "templates"
    MESSAGE = "message"
    PRIMARY_SERVER = "primary_server"
    VALUE = "value"
    USER = "user"
    USER_WALLET = "user_wallet"
    VENDOR_DIR = "vendor_dir"

# Directories
class DDir(StrEnum):
    API = "api_dir"
    BACKUP = "backup_dir"
    BIN = "bin_dir"
    BLOCKCHAIN = "blockchain_dir"
    DATA = DField.DATA_DIR.value
    DB4E = "db4e_dir"
    DEV = "dev_dir"
    INSTALL = DField.INSTALL_DIR.value
    LOG = "log_dir"
    MONEROD = "monerod"
    RUN = "run_dir"
    SRC = "src_dir"
    SYSTEMD = "systemd_dir"
    TEMPLATE = "template_dir"
    TMP_ENVIRON = "DB4E_TMP"
    VENDOR = DField.VENDOR_DIR.value
    CONF = "conf_dir"

# Elements
class DElem(StrEnum):
    DB4E = "db4e"
    INT_P2POOL = "internal_p2pool"
    MONEROD = "monerod"
    MONEROD_REMOTE = "monerod_remote"
    P2POOL = "p2pool"
    P2POOL_REMOTE = "p2pool_remote"
    XMRIG ="xmrig"

# Files
class DFile(StrEnum):
    BACKUP_SCRIPT = "backup_script"
    CONFIG_FILE = DField.CONFIG_FILE
    P2POOL_LOG = "p2pool.log"

# Modules
class DMod(StrEnum):
    DEPLOYMENT_MGR = "DeploymentMgr"
    INSTALL_MGR = "InstallMgr"
    OPS_MGR = "OpsManager"
    PANE_MGR = "PaneMgr"

class Status(StrEnum):
    ERROR = "error"
    GOOD = "good"
    WARN = "warn"


# Fields
ACTIVE_FIELD = "active"
APP_VERSION_FIELD = "app_version"
CHAIN_FIELD = "chain"
COLORTERM_ENVIRON_FIELD = "COLORTERM"
DATA_FIELD = "data"
DEBUG_FIELD = "debug"
DEPLOYMENT_FIELD = "deployment"
DEPLOYMENT_TYPE_FIELD = "depl_type"
DEPLOYMENTS_FIELD = "deployments"
DESC_FIELD = "desc"
DISABLE_FIELD = "disable"
DONATIONS_FIELD = "donations"
ELEMENT_FIELD = "element"
ENABLE_FIELD = "enable"
ENABLED_FIELD = "enabled"
FILE_TYPE_FIELD = "file_type"
HASH_FIELD = "hash"
HEALTH_FIELD = "health"
HEALTH_MSGS_FIELD = "health_msgs"
INFO_MSG_FIELD = "info_msg"
INSTANCE_FIELD = "instance"
LABEL_FIELD = "label"
LEVEL_FIELD = "level"
LOCAL_FIELD = "local"
LOCAL_SOFTWARE_SYSTEM_FIELD = "local_software_system"
LOG_VIEWER_FIELD = "log_viewer"
MACHINE_FIELD = "host"
MESSAGE_FIELD = "message"
MAIN_CHAIN_FIELD = "main_chain"
MINI_CHAIN_FIELD = "mini_chain"
MINER_FIELD = "miner"
MONEROD_ID_FIELD_OLD = "monerod_id"
NAME_FIELD = "name"
NANO_CHAIN_FIELD = "nano_chain"
NEW_FIELD = "new"
NEW_FILE_FIELD = "new_file"
OP_FIELD = "op"
P2POOL_HEALTH_FIELD = "p2pool_health"
P2POOL_ID_FIELD_OLD = "p2pool_id"
P2POOL_INSTANCE = "p2pool_instance"
ORIG_INSTANCE_FIELD = "orig_instance"
PANE_NAME_FIELD = "pane_name"
PARENT_FIELD = "parent"
PARENT_INSTANCE_FIELD = "parent_instance"
PERMISSIONS_FIELD = "permissions"
PLOT_FIELD = "plot"
PLOT_TYPE_FIELD = "plot_type"
PORT_FIELD = "port"
PROCESS_FIELD = "process"
PYPI_REPO_FIELD = "pypi_repo"
PYTHON_FIELD = "python"
REMOTE_FIELD = "remote"
RESET_DATA_FIELD = "reset_data"
RESULTS_FIELD = "results"
SERVER_FIELD = "server"
SET_DATA_FIELD = "set_data"
SET_PANE_FIELD = "set_pane"
SOFTWARE_SYSTEM_FIELD = "software_system"
STARTED_FIELD = "started"
STATUS_FIELD = "status"
TO_MODULE_FIELD = "to_module"
TERM_ENVIRON_FIELD = "TERM"
TIMESTAMP_FIELD = "timestamp"
TO_METHOD_FIELD = "to_method"
TUI_LOG_FIELD = "tui_log"
UNKNOWN_FIELD = "unknown"
UPDATE_FIELD = "update"
VERSION_FIELD = "version"
WALLET_FIELD = "wallet"

# Components
ANY_IP_FIELD = "any_ip"
COMPONENT_FIELD = "component"
DB4E_LOG_FILE_FIELD = "db4e_log_file"
IN_PEERS_FIELD = "in_peers"
INSTALL_DIR_FIELD = DDir.INSTALL.value
IP_ADDR_FIELD = "ip_addr"
LOG_FILE_FIELD = "log_file"
LOG_LEVEL_FIELD = "log_level"
LOG_NAME_FIELD = "log_name"
LOG_RETENTION_DAYS_FIELD = "log_retention_days"
MAX_BACKUPS_FIELD = "max_backups"
MAX_LOG_FILES_FIELD = "max_log_files"
MAX_LOG_SIZE_FIELD = "max_log_size"
MONEROD_LOG_FIELD = "monerod_log"
NUM_THREADS_FIELD = "num_threads"
OUT_PEERS_FIELD = "out_peers"
P2P_BIND_PORT_FIELD = "p2p_bind_port"
P2P_PORT_FIELD = "p2p_port"
PARENT_ID_FIELD = "parent_id"
PRIORITY_NODE_1_FIELD = "priority_node_1"
PRIORITY_NODE_2_FIELD = "priority_node_2"
PRIORITY_PORT_1_FIELD = "priority_port_1"
PRIORITY_PORT_2_FIELD = "priority_port_2"
RADIO_BUTTON_TYPE_FIELD = "radio_button_type"
RADIO_SET_FIELD = "radio_set"
RADIO_MAP_FIELD = "radio_map"
RETRY_TIMEOUT_FIELD = "retry_timeout"
RUN_BACKUP_FIELD = "run_backup"
RPC_BIND_PORT_FIELD = "rpc_bind_port"
SHOW_TIME_STATS_FIELD = "show_time_stats"
SOCKET_FILE_FIELD = "socket_file"
STDIN_FIELD = "stdin"
STRATUM_PORT_FIELD = "stratum_port"
UPDATE_DEPLOYMENT_FIELD = "update_deployment"
VENDOR_DIR_FIELD = DDir.VENDOR.value
ZMQ_PUB_PORT_FIELD = "zmq_pub_port"
ZMQ_RPC_PORT_FIELD = "zmq_rpc_port"


# Mongo
COLLECTION_FIELD = "collection"
CONFIG_FIELD = "config"
DB_FIELD = "db"
DB_NAME_FIELD = "db4e"
DB4E_REFRESH_FIELD = "db4e_refresh"
DEPLOYMENT_COL_FIELD = "depl_collection"
DOC_TYPE_FIELD = "doc_type"
LOG_COLLECTION_FIELD = "log_collection"
METRICS_COLLECTION_FIELD = "metrics_collection"
OBJECT_ID_FIELD = "_id"
TEMPLATES_COLLECTION_FIELD = "templates"

# Methods
ADD_DEPLOYMENT_FIELD = "add_deployment"
DELETE_DEPLOYMENT_FIELD = "del_deployment"
GET_NEW_FIELD = "get_new"
GET_REC_FIELD = "get_deployment"
GET_TUI_LOG_FIELD = "get_tui_log"
INITIAL_SETUP_FIELD = "initial_setup"
SET_PRIMARY_FIELD = "set_primary"




