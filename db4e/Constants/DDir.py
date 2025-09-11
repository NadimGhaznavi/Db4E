"""
db4e/Constants/DDir.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup
from db4e.Constants.DField import DField


# Directories
class DDir(ConstGroup):
    API : str = "api_dir"
    BACKUP : str = "backup_dir"
    BIN : str = "bin_dir"
    BLOCKCHAIN : str = "blockchain_dir"
    DATA : str = DField.DATA_DIR
    DB4E : str = "db4e_dir"
    DEV : str = "dev_dir"
    INSTALL : str = DField.INSTALL_DIR
    LOG : str = "log_dir"
    MONEROD : str = "monerod"
    RUN : str = "run_dir"
    SRC : str = "src_dir"
    SYSTEMD : str = "systemd_dir"
    TEMPLATE : str = "template_dir"
    TMP_ENVIRON : str = "DB4E_TMP"
    VENDOR : str = DField.VENDOR_DIR
    CONF : str = "conf_dir"