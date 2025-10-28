"""
db4e/Constants/DModule.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.util.ConstGroup import ConstGroup


# Modules
class DModule(ConstGroup):
    BASE_ELEM: str = "BaseElem"
    BASE_MONERO: str = "BaseMonero"
    DB4E: str = "Db4E"
    DB4E_SERVER: str = "Db4eServer"
    DEPLOYMENT_DB: str = "DeplDb"
    DEPLOYMENT_CLIENT: str = "DeploymentClient"
    DEPLOYMENT_MGR: str = "DeploymentMgr"
    HEALTH_MGR: str = "HealthMgr"
    INSTALL_MGR: str = "InstallMgr"
    LOCAL_ELEM: str = "LocalElem"
    MINING_DB: str = "MiningDb"
    OPS_DB: str = "OpsDb"
    OPS_MGR: str = "OpsManager"
    P2POOL_WATCHER: str = "P2PoolWatcher"
    PANE_MGR: str = "PaneMgr"
    SQL_DB: str = "SQLDb"
    XMRIG: str = "XMRig"
