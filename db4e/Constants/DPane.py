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
    CHAIN_ANALYTICS : str = "ChainAnalyticsPane"
    CHAIN_HASHRATES : str = "ChainHashratesPane"
    DB4E: str = "Db4EPane"
    DONATIONS: str  = "DonationsPane"
    INITIAL_SETUP: str  = "InitialSetupPane"
    LOG_VIEW: str  = "LogViewPane"
    MONEROD_TYPE: str  = "MoneroDTypePane"
    MONEROD: str  = "MoneroDPane"
    MONEROD_REMOTE: str  = "MoneroDRemotePane"
    P2POOL_TYPE: str  = "P2PoolTypePane"
    P2POOL: str  = "P2PoolPane"
    P2POOL_ANALYTICS: str  = "P2PoolAnalyticsPane"
    P2POOL_HASHRATES: str  = "P2PoolHashratesPane"
    CHAIN: str  = "ChainPane"
    P2POOL_REMOTE: str  = "P2PoolRemotePane"
    RESULTS: str  = "ResultsPane"
    RUNTIME_LOG: str  = "RuntimeLogPane"
    TUI_LOG: str  = "TuiLogPane"
    UPTIME: str  = "UptimePane"
    WELCOME: str  = "WelcomePane"
    XMRIG: str  = "XMRigPane"
    XMRIG_HASHRATES: str  = "XMRigHashratesPane"
    XMRIG_REMOTE: str  = "XMRigRemotePane"