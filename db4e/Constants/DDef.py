"""
db4e/Constants/DDef.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup

class DDef(ConstGroup):
    ANY_IP: str = "0.0.0.0"
    API_DIR: str = "api"
    APP_TITLE: str  = "Db4E"
    BACKUP_DIR: str  = "backups"
    BACKUP_SCRIPT: str  = "db4e-backup.sh"
    BIN_DIR: str  = "bin"
    BLOCKCHAIN_DIR: str  = "blockchain"
    COLORTERM: str  = "truecolor"
    CONF_DIR: str  = "conf"
    CSS_PATH: str  = "Db4E.tcss"
    DB_NAME: str  = "db4e"
    DB_PORT: int = 27017
    DB_RETRY_TIMEOUT: int = 3000
    DB_SERVER: str  = "localhost"
    DB4E_DIR: str  = "db4e"
    DB4E_INITIAL_SETUP_SCRIPT: str  = "db4e-initial-setup.sh"
    DB4E_INSTALL_SERVICE: str  = "db4e-install-service.sh"
    DB4E_LOG_FILE: str  = "db4e.log"
    DB4E_LOGGER: str  = "Db4eLogger"
    DB4E_OLD_GROUP_ENVIRON: str  = "DB4E_OLD_GROUP"
    DB4E_PROCESS: str  = "db4e"
    DB4E_REFRESH: int  = 15
    DB4E_SERVICE_FILE: str = "db4e.service"
    DB4E_START_SCRIPT: str = "db4e-server"
    DB4E_UNINSTALL_SCRIPT: str = "db4e-uninstall-service.sh"
    DB4E_VERSION: str = "0.41.0"
    DEPLOYMENT_COL: str = "depl"
    DEV_DIR: str = "dev"
    DONATION_WALLET: str = "48aTDJfRH2JLcKW2fz4m9HJeLLVK5rMo1bKiNHFc43Ht2e2kPVh2tmk3Md7npz1WsSU7bpgtX2Xnf59RHCLUEaHfQHwao4j"
    IN_PEERS: int = 16
    INI_SUFFIX: str = ".ini"
    INITIAL_SETUP: str = "db4e-initial-setup.sh"
    JOBS_COL: str = "jobs"
    JSON_SUFFIX: str = ".json"
    LOCALHOST: str = "127.0.0.1"
    LOG_DIR: str = "logs"
    LOG_LEVEL: int = 0
    LOG_COLLECTION: str = "logging"
    LOG_RETENTION_DAYS: int = 7
    LOG_SUFFIX: str = ".log"
    MAX_BACKUPS: int = 7
    MAX_LOG_FILES: int = 7
    MAX_LOG_LINES: int = 500
    MAX_LOG_SIZE: int = 100000
    METRICS_COLLECTION: str = "metrics"
    MINING_COL: str = "mining"
    MONEROD_CONFIG: str = "monerod.ini"
    MONEROD_DIR: str = "monerod"
    MONEROD_LOG_FILE: str = "monerod.log"
    MONEROD_PROCESS: str = "monerod"
    MONEROD_SERVICE_FILE: str = "monerod@.service"
    MONEROD_SOCKET_SERVICE: str = "monerod@.socket"
    MONEROD_STDIN_PIPE: str = "monerod.stdin"
    MONEROD_START_SCRIPT: str = "start-monerod.sh"
    MONEROD_VERSION: str = "0.18.4.2"
    NUM_THREADS: int = 1
    OPS_COL: str = "ops"
    P2P_DIR: str = "p2p"
    OUT_PEERS: int = 16
    P2P_BIND_PORT: int = 18080
    P2P_PORT: int = 37889
    P2POOL_CONFIG: str = "p2pool.ini"
    P2POOL_DIR: str = "p2pool"
    P2POOL_LOG_FILE: str = "p2pool.log"
    P2POOL_PROCESS: str = "p2pool"
    P2POOL_SERVICE_FILE: str = "p2pool@.service"
    P2POOL_SERVICE_SOCKET_FILE: str = "p2pool@.socket"
    P2POOL_START_SCRIPT: str = "start-p2pool.sh"
    P2POOL_STDIN_PIPE: str = "p2pool.stdin"
    P2POOL_VERSION: str = "4.10.1"
    PRIORITY_NODE_1: str = "p2pmd.xmrvsbeast.com"
    PRIORITY_NODE_2: str = "nodes.hashvault.pro"
    PYPI_REPO: str = 'https://pypi.org/pypi/db4e/json'
    PYTHON: str = "python"
    RPC_BIND_PORT: int = 18081
    RUN_DIR: str = "run"
    SERVICE_STATUS: str = "stopped"
    SHOW_TIME_STATS: int = 1
    SRC_DIR: str = "src"
    STRATUM_PORT: int = 3333
    SUDO_CMD: str = "sudo"
    SYSTEMD_DIR: str = "systemd"
    TEMPLATES_DIR: str = "Templates"
    TEMPLATES_COLLECTION: str = "templates"
    TERM: str = "xterm-256color"
    TMP_DIR: str = "/tmp"
    VENDOR_DIR: str = "vendor"
    XMRIG_CONF_DIR: str = "conf"
    XMRIG_CONFIG: str = "config.json"
    XMRIG_DIR: str = "xmrig"
    XMRIG_PERMISSIONS: str = "-rwsr-x---"
    XMRIG_PROCESS: str = "xmrig"
    XMRIG_SERVICE_FILE: str = "xmrig@.service"
    XMRIG_VERSION: str = "6.24.0"
    ZMQ_PUB_PORT: int = 18083
    ZMQ_RPC_PORT: int = 18082

