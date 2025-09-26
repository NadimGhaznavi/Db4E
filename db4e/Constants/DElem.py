"""
db4e/Constants/DElem.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup

# Elements
class DElem(ConstGroup):
    DB4E : str = "db4e"
    INT_P2POOL : str = "internal_p2pool"
    MONEROD : str = "monerod"
    MONEROD_REMOTE : str = "monerod_remote"
    P2POOL : str = "p2pool"
    P2POOL_WATCHER : str = "p2pool_watcher"
    P2POOL_REMOTE : str = "p2pool_remote"
    XMRIG : str = "xmrig"
    XMRIG_REMOTE : str = "xmrig_remote"