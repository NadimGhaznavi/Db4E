# db4e/Constants/DDef.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from typing import Final


class DDef:
    ANY_IP: Final[str] = "0.0.0.0"
    API_DIR: Final[str] = "api"
    API_PORT: Final[int] = 8888
    APP_TITLE: Final[str] = "Db4E"
    BACKUP_DIR: Final[str] = "backups"
    BACKUP_SCRIPT: Final[str] = "db4e-backup.sh"
    BIN_DIR: Final[str] = "bin"
    BLOCKCHAIN_DIR: Final[str] = "blockchain"
    COLORTERM: Final[str] = "truecolor"
    CONF_DIR: Final[str] = "conf"
    CONF_SUFFIX: Final[str] = ".conf"
    CSS_PATH: Final[str] = "Db4E.tcss"
    DB_DIR: Final[str] = "db"
    DB_NAME: Final[str] = "db4e"
    DB_PORT: Final[int] = 27017
    DB_RETRY_TIMEOUT: Final[int] = 3000
    DB_SERVER: Final[str] = "localhost"
    DB4E_DIR: Final[str] = "db4e"
    DB4E_INITIAL_SETUP_SCRIPT: Final[str] = "db4e-initial-setup.sh"
    DB4E_INSTALL_SERVICE: Final[str] = "db4e-install-service.sh"
    DB4E_LOG_FILE: Final[str] = "db4e.log"
    DB4E_LOGGER: Final[str] = "Db4eLogger"
    DB4E_OLD_GROUP_ENVIRON: Final[str] = "DB4E_OLD_GROUP"
    DB4E_PROCESS: Final[str] = "db4e"
    DB4E_REFRESH: Final[int] = 15
    DB4E_SERVICE_FILE: Final[str] = "db4e.service"
    DB4E_START_SCRIPT: Final[str] = "db4e-server"
    DB4E_UNINSTALL_SCRIPT: Final[str] = "db4e-uninstall-service.sh"
    DB4E_VERSION: Final[str] = "0.48.1"
    DEPL_COLLECTION: Final[str] = "depl"
    DEV_DIR: Final[str] = "dev"
    DONATION_WALLET: Final[str] = (
        "48aTDJfRH2JLcKW2fz4m9HJeLLVK5rMo1bKiNHFc43Ht2e2kPVh2tmk3Md7npz1WsSU7bpgtX2Xnf59RHCLUEaHfQHwao4j"
    )
    GZIP_SUFFIX: Final[str] = ".gz"
    IN_PEERS: Final[int] = 16
    INI_SUFFIX: Final[str] = ".ini"
    INITIAL_SETUP: Final[str] = "db4e-initial-setup.sh"
    JOBS_COLLECTION: Final[str] = "jobs"
    JSON_SUFFIX: Final[str] = ".json"
    LOCALHOST: Final[str] = "127.0.0.1"
    LOG_DIR: Final[str] = "logs"
    LOG_LEVEL: Final[int] = 0
    LOG_COLLECTION: Final[str] = "logging"
    LOG_RETENTION_DAYS: Final[int] = 7
    LOG_SUFFIX: Final[str] = ".log"
    LOGROTATE: Final[str] = "logrotate"
    MAX_BACKUPS: Final[int] = 7
    MAX_LOG_FILES: Final[int] = 7
    MAX_LOG_LINES: Final[int] = 500
    MAX_LOG_SIZE: Final[int] = 10000000
    MINING_COLLECTION: Final[str] = "mining"
    MONEROD_CONFIG: Final[str] = "monerod.ini"
    MONEROD_DIR: Final[str] = "monerod"
    MONEROD_LOG_FILE: Final[str] = "monerod.log"
    MONEROD_PROCESS: Final[str] = "monerod"
    MONEROD_SERVICE_FILE: Final[str] = "monerod@.service"
    MONEROD_SOCKET_SERVICE: Final[str] = "monerod@.socket"
    MONEROD_STDIN_PIPE: Final[str] = "monerod.stdin"
    MONEROD_START_SCRIPT: Final[str] = "start-monerod.sh"
    MONEROD_VERSION: Final[str] = "0.18.4.2"
    NUM_THREADS: Final[int] = 1
    OPS_COLLECTION: Final[str] = "ops"
    P2P_DIR: Final[str] = "p2p"
    OUT_PEERS: Final[int] = 16
    P2P_BIND_PORT: Final[int] = 18080
    P2P_PORT: Final[int] = 37889
    P2POOL_CONFIG: Final[str] = "p2pool.ini"
    P2POOL_DIR: Final[str] = "p2pool"
    P2POOL_LOG_FILE: Final[str] = "p2pool.log"
    P2POOL_PROCESS: Final[str] = "p2pool"
    P2POOL_SERVICE_FILE: Final[str] = "p2pool@.service"
    P2POOL_SERVICE_SOCKET_FILE: Final[str] = "p2pool@.socket"
    P2POOL_START_SCRIPT: Final[str] = "start-p2pool.sh"
    P2POOL_STDIN_PIPE: Final[str] = "p2pool.stdin"
    P2POOL_VERSION: Final[str] = "4.11"
    PRIORITY_NODE_1: Final[str] = "p2pmd.xmrvsbeast.com"
    PRIORITY_NODE_2: Final[str] = "nodes.hashvault.pro"
    PYPI_REPO: Final[str] = "https://pypi.org/pypi/db4e/json"
    PYTHON: Final[str] = "python"
    ROOT: Final[str] = "root"
    RPC_BIND_PORT: Final[int] = 18081
    RUN_DIR: Final[str] = "run"
    SERVICE_STATUS: Final[str] = "stopped"
    SHOW_TIME_STATS: Final[int] = 1
    SRC_DIR: Final[str] = "src"
    STRATUM_PORT: Final[int] = 3333
    SUDO_CMD: Final[str] = "sudo"
    SYSTEMD_DIR: Final[str] = "systemd"
    TEMPLATES_DIR: Final[str] = "templates"
    TERM: Final[str] = "xterm-256color"
    TMP_DIR: Final[str] = "/tmp"
    VENDOR_DIR: Final[str] = "vendor"
    XMRIG_CONF_DIR: Final[str] = "conf"
    XMRIG_CONFIG: Final[str] = "config.json"
    XMRIG_DIR: Final[str] = "xmrig"
    XMRIG_DIV: Final[str] = "NaDiM"
    XMRIG_PERMISSIONS: Final[str] = "-rwsr-x---"
    XMRIG_PROCESS: Final[str] = "xmrig"
    XMRIG_SERVICE_FILE: Final[str] = "xmrig@.service"
    XMRIG_VERSION: Final[str] = "6.24.0"
    ZMQ_PUB_PORT: Final[int] = 18083
    ZMQ_RPC_PORT: Final[int] = 18082
