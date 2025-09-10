"""
db4e/Constants/Panes.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from enum import StrEnum


class Pane(StrEnum):
    DB4E = "Db4EPane"
    DONATIONS = "DonationsPane"
    INITIAL_SETUP = "InitialSetupPane"
    LOG_VIEW = "LogViewPane"
    MONEROD_TYPE = "MoneroDTypePane"
    MONEROD = "MoneroDPane"
    MONEROD_REMOTE = "MoneroDRemotePane"
    P2POOL_TYPE = "P2PoolTypePane"
    P2POOL = "P2PoolPane"
    P2POOL_REMOTE = "P2PoolRemotePane"
    PLOT_VIEW = "PlotViewPane"
    XMRIG = "XMRigPane"
    RESULTS = "ResultsPane"
    TUI_LOG = "TuiLogPane"
    WELCOME = "WelcomePane"
    XMRIG = "XMRigPane"