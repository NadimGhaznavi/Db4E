"""
db4e/Constants/Defaults.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from enum import StrEnum

class DDef(StrEnum):
    ANY_IP = "0.0.0.0"
    API_DIR = "api"
    APP_TITLE = "Db4E"
    BACKUP_DIR = "backups"
    BACKUP_SCRIPT = "db4e-backup.sh"
    BIN_DIR = "bin"
    BLOCKCHAIN_DIR = "monero-blockchain"
    CHAIN = "mini"
    COLORTERM = "truecolor"
    CONF_DIR = "conf"
    CSS_PATH = "Db4E.tcss"
    DB_NAME = "db4e"
    DB_PORT = 27017
    DB_RETRY_TIMEOUT = 3000
    DB_SERVER = "localhost"
    DB4E_DIR = "db4e"
    DB4E_INITIAL_SETUP_SCRIPT = "db4e-initial-setup.sh"
    DB4E_INSTALL_SERVICE = "db4e-install-service.sh"
    DB4E_LOG_FILE = "db4e.log"
    DB4E_LOGGER = "Db4eLogger"
    DB4E_OLD_GROUP_ENVIRON = "DB4E_OLD_GROUP"
    DB4E_PROCESS = "db4e"
    DB4E_REFRESH = 15
    DB4E_SERVER = "Db4eServer"
    DB4E_SERVICE_FILE = "db4e.service"
    DB4E_START_SCRIPT = "db4e-server"
    DB4E_UNINSTALL_SCRIPT = "db4e-uninstall-service.sh"
    DB4E_VERSION = "0.35.0"
    DEPLOYMENT_COL = "depl"
    DEV_DIR = "dev"
    DONATION_WALLET = "48aTDJfRH2JLcKW2fz4m9HJeLLVK5rMo1bKiNHFc43Ht2e2kPVh2tmk3Md7npz1WsSU7bpgtX2Xnf59RHCLUEaHfQHwao4j"
    IN_PEERS = 16
    INITIAL_SETUP = "db4e-initial-setup.sh"
    LOCALHOST = "127.0.0.1"
    LOG_DIR = "logs"
    LOG_LEVEL = 0
    LOG_COLLECTION = "logging"
    LOG_RETENTION_DAYS = 7
    MAX_BACKUPS = 7
    MAX_LOG_FILES = 7
    MAX_LOG_LINES = 500
    MAX_LOG_SIZE = 100000
    METRICS_COLLECTION = "metrics"
    MINING_COL = "mining"
    MONEROD_CONFIG = "monerod.ini"
    MONEROD_LOG_FILE = "monerod.log"
    MONEROD_PROCESS = "monerod"
    MONEROD_SERVICE_FILE = "monerod@.service"
    MONEROD_SOCKET_SERVICE = "monerod@.socket"
    MONEROD_STDIN_PIPE = "monerod.stdin"
    MONEROD_START_SCRIPT = "start-monerod.sh"
    MONEROD_VERSION = "0.18.4.2"
    NUM_THREADS = 1
    OPS_COL = "ops"
    OUT_PEERS = 16
    P2P_BIND_PORT = 18080
    P2P_PORT = 37889
    P2POOL_CONFIG = "p2pool.ini"
    P2POOL_LOG_FILE = "p2pool.log"
    P2POOL_PROCESS = "p2pool"
    P2POOL_SERVICE_FILE = "p2pool@.service"
    P2POOL_SERVICE_SOCKET_FILE = "p2pool@.socket"
    P2POOL_START_SCRIPT = "start-p2pool.sh"
    P2POOL_STDIN_PIPE = "p2pool.stdin"
    P2POOL_VERSION = "4.9.1"
    PRIORITY_NODE_1 = "p2pmd.xmrvsbeast.com"
    PRIORITY_NODE_2 = "nodes.hashvault.pro"
    PYPI_REPO = 'https://pypi.org/pypi/db4e/json'
    PYTHON = "python"
    RPC_BIND_PORT = 18081
    RUN_DIR = "run"
    SERVICE_STATUS = "stopped"
    SHOW_TIME_STATS = 1
    SRC_DIR = "src"
    STRATUM_PORT = 3333
    SUDO_CMD = "sudo"
    SYSTEMD_DIR = "systemd"
    TEMPLATES_DIR = "Templates"
    TEMPLATES_COLLECTION = "templates"
    TERM = "xterm-256color"
    TMP_DIR = "/tmp"
    VENDOR_DIR = "vendor"
    XMRIG_CONF_DIR = "conf"
    XMRIG_CONFIG = "config.json"
    XMRIG_PERMISSIONS = "-rwsr-x---"
    XMRIG_PROCESS = "xmrig"
    XMRIG_SERVICE_FILE = "xmrig@.service"
    XMRIG_VERSION = "6.24.0"
    ZMQ_PUB_PORT = 18083
    ZMQ_RPC_PORT = 18082

