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
    ACTIVE = "active"
    ANY_IP = "any_ip"
    APP_VERSION = "app_version"
    CHAIN = "chain"
    COLORTERM_ENVIRON = "COLORTERM"
    COMPONENT = "component"
    COMPONENTS = "components"
    CONFIG_FILE = "config_file"
    DATA = "data"
    DATA_DIR = "data_dir"
    DB4E_LOG_FILE = "db4e_log_file"
    DEBUG = "debug"
    DEPLOYMENT = "deployment"
    DEPLOYMENT_TYPE = "depl_type"
    DEPLOYMENTS = "deployments"
    DESC = "desc"
    DISABLE = "disable"
    DONATIONS = "donations"
    DONATION_WALLET = "donation_wallet"
    ELEMENT = "element"
    ELEMENT_TYPE = "element_type"
    ENABLE = "enable"
    ENABLED = "enabled"
    FIELD = "field"
    FILE_TYPE = "file_type"
    GROUP = "group"
    HASH = "hash"
    HEALTH = "health"
    HEALTH_MSGS = "health_msgs"
    IN_PEERS = "in_peers"
    INFO_MSG = "info_msg"
    INSTALL_DIR = "install_dir"
    INSTANCE = "instance"
    IP_ADDR = "ip_addr"
    LABEL = "label"
    LEVEL = "level"
    LOCAL = "local"
    LOCAL_SOFTWARE_SYSTEM = "local_software_system"
    LOG_FILE = "log_file"
    LOG_LEVEL = "log_level"
    LOG_NAME = "log_name"
    LOG_RETENTION_DAYS = "log_retention_days"
    LOG_VIEWER = "log_viewer"
    MACHINE = "host"
    MAX_BACKUPS = "max_backups"
    MAX_LOG_FILES = "max_log_files"
    MAX_LOG_SIZE = "max_log_size"
    MESSAGE = "message"
    MAIN_CHAIN = "main_chain"
    MINI_CHAIN = "mini_chain"
    MINER = "miner"
    MONEROD_ID_OLD = "monerod_id"
    MONEROD_LOG = "monerod_log"
    NAME = "name"
    NANO_CHAIN = "nano_chain"
    NEW = "new"
    NEW_FILE = "new_file"
    NUM_THREADS = "num_threads"
    OBJECT_ID = "_id"
    OP = "op"
    P2P_BIND_PORT = "p2p_bind_port"
    P2P_PORT = "p2p_port"
    P2POOL_HEALTH = "p2pool_health"
    P2POOL_ID_OLD = "p2pool_id"
    P2POOL_INSTANCE = "p2pool_instance"
    PRIMARY_SERVER = "primary_server"
    ORIG_INSTANCE = "orig_instance"
    OUT_PEERS = "out_peers"
    PANE_NAME = "pane_name"
    PARENT = "parent"
    PARENT_ID = "parent_id"
    PARENT_INSTANCE = "parent_instance"
    PERMISSIONS = "permissions"
    PLOT = "plot"
    PLOT_TYPE = "plot_type"
    PORT = "port"
    PRIORITY_NODE_1 = "priority_node_1"
    PRIORITY_NODE_2 = "priority_node_2"
    PRIORITY_PORT_1 = "priority_port_1"
    PRIORITY_PORT_2 = "priority_port_2"
    PROCESS = "process"
    PYPI_REPO = "pypi_repo"
    PYTHON = "python"
    RADIO_MAP = "radio_map"
    REMOTE = "remote"
    RESET_DATA = "reset_data"
    RESULTS = "results"
    RETRY_TIMEOUT = "retry_timeout"
    RUN_BACKUP = "run_backup"
    RPC_BIND_PORT = "rpc_bind_port"
    SHOW_TIME_STATS = "show_time_stats"
    SERVER = "server"
    SET_DATA = "set_data"
    SET_PANE = "set_pane"
    SOCKET_FILE = "socket_file"
    STDIN = "stdin"
    STRATUM_PORT = "stratum_port"
    SOFTWARE_SYSTEM = "software_system"
    STARTED = "started"
    STATUS = "status"
    TEMPLATE = "template"
    TEMPLATES = "templates"
    TO_MODULE = "to_module"
    TERM_ENVIRON = "TERM"
    TIMESTAMP = "timestamp"
    TO_METHOD = "to_method"
    TUI_LOG = "tui_log"
    UNKNOWN = "unknown"
    UPDATE = "update"
    USER = "user"
    USER_WALLET = "user_wallet"
    UPDATE_DEPLOYMENT = "update_deployment"
    VENDOR_DIR = "vendor_dir"
    VALUE = "value"
    VENDOR_DIR = "vendor_dir"
    VERSION = "version"
    WALLET = "wallet"
    ZMQ_PUB_PORT = "zmq_pub_port"
    ZMQ_RPC_PORT = "zmq_rpc_port"


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
    CONFIG_FILE = DField.CONFIG_FILE.value
    P2POOL_LOG = "p2pool.log"

# Modules
class DMod(StrEnum):
    DEPLOYMENT_MGR = "DeploymentMgr"
    INSTALL_MGR = "InstallMgr"
    OPS_MGR = "OpsManager"
    PANE_MGR = "PaneMgr"

# Status
class Status(StrEnum):
    ERROR = "error"
    GOOD = "good"
    WARN = "warn"

# Methods
class Method(StrEnum):
    ADD_DEPLOYMENT = "add_deployment"
    DELETE_DEPLOYMENT = "del_deployment"
    GET_NEW = "get_new"
    GET_REC = "get_deployment"
    GET_TUI_LOG = "get_tui_log"
    INITIAL_SETUP = "initial_setup"
    LOG_VIEWER = DField.LOG_VIEWER.value
    PLOT = "plot"
    POST_JOB = "post_job"
    SET_PANE = DField.SET_PANE.value
    SET_PRIMARY = "set_primary"

# Mongo
class Mongo(StrEnum):
    COLLECTION = "collection"
    CONFIG = "config"
    DB = "db"
    DB_NAME = "db4e"
    DB4E_REFRESH = "db4e_refresh"
    DEPLOYMENT_COL = "depl_collection"
    DOC_TYPE = "doc_type"
    LOG_COLLECTION = "log_collection"
    METRICS_COLLECTION = "metrics_collection"
    MINER = DField.MINER.value
    OBJECT_ID = DField.OBJECT_ID.value
    TEMPLATES_COLLECTION = "templates"
    TIMESTAMP = DField.TIMESTAMP.value













