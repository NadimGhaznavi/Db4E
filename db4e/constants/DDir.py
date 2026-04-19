# db4e/Constants/DDir.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from typing import Final

from db4e.constants.DField import DField
from db4e.constants.DDef import DDef
from db4e.constants.DFile import DFile


# Directories
class DDir:
    API: Final[str] = "api_dir"
    BACKUP: Final[str] = "backup_dir"
    BIN: Final[str] = "bin_dir"
    BLOCKCHAIN: Final[str] = DDef.BLOCKCHAIN_DIR
    CONF: Final[str] = "conf_dir"
    DATA: Final[str] = DField.DATA_DIR
    DB: Final[str] = "db_dir"
    DB4E: Final[str] = "db4e_dir"
    DEV: Final[str] = "dev_dir"
    DOT_DB4E: Final[str] = ".db4e"
    INSTALL: Final[str] = DField.INSTALL_DIR
    LOG: Final[str] = "log_dir"
    LOGROTATE: Final[str] = DFile.LOGROTATE
    MONEROD: Final[str] = "monerod"
    P2POOL: Final[str] = "p2pool"
    RUN: Final[str] = "run_dir"
    SRC: Final[str] = "src_dir"
    SYSTEMD: Final[str] = "systemd_dir"
    TEMPLATE: Final[str] = "template_dir"
    TMP: Final[str] = "tmp"
    TMP_ENVIRON: Final[str] = "DB4E_TMP"
    VENDOR: Final[str] = DField.VENDOR_DIR
    XMRIG: Final[str] = "xmrig"
