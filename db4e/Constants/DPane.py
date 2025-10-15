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
    CHAIN: str = "ChainPane"
    CHAIN_BLOCKS_FOUND: str = "ChainBlocksFoundPane"
    CHAIN_HASHRATES: str = "ChainHashratesPane"
    DB4E: str = "Db4EPane"
    DONATIONS: str = "DonationsPane"
    INITIAL_SETUP: str = "InitialSetupPane"
    LOG_VIEW: str = "LogViewPane"
    MONEROD_TYPE: str = "MoneroDTypePane"
    MONEROD: str = "MoneroDPane"
    MONEROD_REMOTE: str = "MoneroDRemotePane"
    P2POOL_TYPE: str = "P2PoolTypePane"
    P2POOL: str = "P2PoolPane"
    P2POOL_ANALYTICS: str = "P2PoolAnalyticsPane"
    P2POOL_HASHRATES: str = "P2PoolHashratesPane"
    P2POOL_REMOTE: str = "P2PoolRemotePane"
    P2POOL_SHARES_FOUND: str = "P2PoolSharesFoundPane"
    P2POOL_TABLES: str = "P2PoolTablesPane"
    PAYMENTS: str = "PaymentsPane"
    RESULTS: str = "ResultsPane"
    RUNTIME_LOG: str = "RuntimeLogPane"
    TUI_LOG: str = "TuiLogPane"
    START_STOP_LOG: str = "StartStopLogPane"
    WELCOME: str = "WelcomePane"
    XMRIG: str = "XMRigPane"
    XMRIG_HASHRATES: str = "XMRigHashratesPane"
    XMRIG_REMOTE: str = "XMRigRemotePane"
    XMRIG_REMOTE_HASHRATES: str = "XMRigRemoteHashratePane"
    XMRIG_SHARES_FOUND: str = "XMRigSharesFoundPane"
