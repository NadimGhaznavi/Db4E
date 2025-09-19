"""
db4e/Constants/DModule.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup

# Modules
class DModule(ConstGroup):
    DB4E_SERVER: str = "Db4eServer"
    DEPLOYMENT_CLIENT : str = "DeploymentClient"
    DEPLOYMENT_MGR : str = "DeploymentMgr"
    INSTALL_MGR : str = "InstallMgr"
    MINING_DB : str = "MiningDb"
    OPS_MGR : str = "OpsManager"
    PANE_MGR : str = "PaneMgr"