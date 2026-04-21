# db4e/Constants/DFile.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    Website: https://db4e.osoyalce.com/
#    License: GPL 3.0


from typing import Final
from db4e.constants.DField import DField


# Files
class DFile:
    BACKUP_SCRIPT: Final[str] = "backup_script"
    BOOTSTRAP: Final[str] = "bootstrap"
    CHOWN: Final[str] = "chown"
    CLIENT_DB: Final[str] = "client.db"
    CONFIG: Final[str] = DField.CONFIG_FILE
    LOGROTATE: Final[str] = "logrotate"
    MONGODUMP: Final[str] = "mongodump"
    P2POOL_LOG: Final[str] = "p2pool.log"
    P2POOL_STDIN: Final[str] = "p2pool.stdin"
    PYTHON: Final[str] = "python"
    RM: Final[str] = "rm"
    SCRIPT: Final[str] = "script"
    SERVER_DB: Final[str] = "server.db"
    STATS_MOD: Final[str] = "stats_mod"
    SUDO: Final[str] = "sudo"
    SUDO_TEST: Final[str] = "sudo_test.sh"
    SYSTEMCTL: Final[str] = "systemctl"
    UVICORN_LOG: Final[str] = "uvicorn.log"
