"""
db4e/Constants/DPlaceholder.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Used to generate the systemd service definition files in the InstallMgr using
service definition templates.
"""

from db4e.Modules.ConstGroup import ConstGroup

class DPlaceholder(ConstGroup):
    DB4E_USER : str = "DB4E_USER"
    DB4E_GROUP : str = "DB4E_GROUP"
    DB4E_DIR : str = "DB4E_DIR"
    INSTALL_DIR : str = "INSTALL_DIR"
    MONEROD_DIR : str = "MONEROD_DIR"
    P2POOL_DIR : str = "P2POOL_DIR"
    PYTHON : str = "PYTHON"
    XMRIG_DIR : str = "XMRIG_DIR"