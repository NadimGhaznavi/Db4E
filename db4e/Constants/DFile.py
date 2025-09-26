"""
db4e/Constants/DFile.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup
from db4e.Constants.DField import DField


# Files
class DFile(ConstGroup):
    BACKUP_SCRIPT : str = "backup_script"
    CONFIG_FILE : str = DField.CONFIG_FILE
    P2POOL_LOG : str = "p2pool.log"
    P2POOL_STDIN : str = "p2pool.stdin"
    STATS_MOD : str = "stats_mod"
    SUDO : str = "sudo"
    SYSTEMCTL : str = "systemctl"