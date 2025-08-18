"""
db4e/Modules/PaneCatalogue.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container

from db4e.Panes.Db4EPane import Db4EPane
from db4e.Panes.DonationsPane import DonationsPane
from db4e.Panes.InitialSetupPane import InitialSetupPane
from db4e.Panes.MoneroDPane import MoneroDPane
from db4e.Panes.MoneroDRemotePane import MoneroDRemotePane
from db4e.Panes.MoneroDTypePane import MoneroDTypePane
from db4e.Panes.P2PoolPane import P2PoolPane
from db4e.Panes.P2PoolRemotePane import P2PoolRemotePane
from db4e.Panes.P2PoolTypePane import P2PoolTypePane
from db4e.Panes.ResultsPane import ResultsPane
from db4e.Panes.TUILogPane import TUILogPane
from db4e.Panes.WelcomePane import WelcomePane
from db4e.Panes.XMRigPane import XMRigPane


from db4e.Constants.Labels import (
    CONFIG_LABEL, DB4E_LABEL, DB4E_LONG_LABEL, DONATIONS_LABEL, INITIAL_SETUP_LABEL,
    MONEROD_LABEL, MONEROD_REMOTE_LABEL, P2POOL_LABEL, P2POOL_REMOTE_LABEL,
    RESULTS_LABEL, WELCOME_LABEL, XMRIG_LABEL, TUI_LOG_LABEL, LOG_LABEL
)
from db4e.Constants.Panes import (
    DB4E_PANE, DONATIONS_PANE, INITIAL_SETUP_PANE, MONEROD_REMOTE_PANE, 
    MONEROD_PANE, MONEROD_TYPE_PANE, P2POOL_PANE, P2POOL_TYPE_PANE, 
    P2POOL_REMOTE_PANE, RESULTS_PANE, WELCOME_PANE, XMRIG_PANE, TUI_LOG_PANE
)
from db4e.Constants.Buttons import (
    NEW_LABEL
)


REGISTRY = {
    DB4E_PANE: (Db4EPane, DB4E_LONG_LABEL, DB4E_LABEL),
    DONATIONS_PANE: (DonationsPane, DONATIONS_LABEL, DONATIONS_LABEL),
    INITIAL_SETUP_PANE: (InitialSetupPane, DB4E_LONG_LABEL, INITIAL_SETUP_LABEL),
    MONEROD_TYPE_PANE: (MoneroDTypePane, MONEROD_LABEL, NEW_LABEL),
    MONEROD_PANE: (MoneroDPane, MONEROD_LABEL, NEW_LABEL),
    MONEROD_REMOTE_PANE: (MoneroDRemotePane, MONEROD_REMOTE_LABEL, CONFIG_LABEL),
    P2POOL_TYPE_PANE: (P2PoolTypePane, P2POOL_LABEL, NEW_LABEL),
    P2POOL_PANE: (P2PoolPane, P2POOL_LABEL, NEW_LABEL),
    P2POOL_REMOTE_PANE: (P2PoolRemotePane, P2POOL_REMOTE_LABEL, CONFIG_LABEL),
    XMRIG_PANE: (XMRigPane, XMRIG_LABEL, NEW_LABEL),
    RESULTS_PANE: (ResultsPane, DB4E_LONG_LABEL, RESULTS_LABEL),
    TUI_LOG_PANE: (TUILogPane, LOG_LABEL, TUI_LOG_LABEL),
    WELCOME_PANE: (WelcomePane, DB4E_LONG_LABEL, WELCOME_LABEL),
}

class PaneCatalogue:

    def __init__(self):
        self.registry = REGISTRY

    def get_pane(self, pane_name: str, pane_data=None) -> Container:
        pane_class, _, _ = self.registry[pane_name]
        return pane_class(id=pane_name, data=pane_data) if pane_data else pane_class(id=pane_name)

    def get_metadata(self, pane_name: str) -> tuple[str, str]:
        _, component, msg = self.registry.get(pane_name, (None, "", ""))
        return component, msg