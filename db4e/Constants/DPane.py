"""
db4e/Constants/DPanes.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from db4e.Modules.ConstGroup import ConstGroup


class DPane(ConstGroup):
    DB4E: str = "Db4EPane"
    DONATIONS: str  = "DonationsPane"
    INITIAL_SETUP: str  = "InitialSetupPane"
    LOG_VIEW: str  = "LogViewPane"
    MONEROD_TYPE: str  = "MoneroDTypePane"
    MONEROD: str  = "MoneroDPane"
    MONEROD_REMOTE: str  = "MoneroDRemotePane"
    P2POOL_TYPE: str  = "P2PoolTypePane"
    P2POOL: str  = "P2PoolPane"
    P2POOL_REMOTE: str  = "P2PoolRemotePane"
    PLOT_VIEW: str  = "PlotViewPane"
    RESULTS: str  = "ResultsPane"
    TUI_LOG: str  = "TuiLogPane"
    WELCOME: str  = "WelcomePane"
    XMRIG: str  = "XMRigPane"
    XMRIG_REMOTE: str  = "XMRigRemotePane"