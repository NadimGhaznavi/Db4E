"""
db4e/Modules/PaneCatalogue.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container

from db4e.Panes.ChainHashratesPane import ChainHashratesPane
from db4e.Panes.Db4EPane import Db4EPane
from db4e.Panes.DonationsPane import DonationsPane
from db4e.Panes.InitialSetupPane import InitialSetupPane
from db4e.Panes.LogViewPane import LogViewPane
from db4e.Panes.MoneroDPane import MoneroDPane
from db4e.Panes.MoneroDRemotePane import MoneroDRemotePane
from db4e.Panes.P2PoolPane import P2PoolPane
from db4e.Panes.P2PoolHashratesPane import P2PoolHashratesPane
from db4e.Panes.ChainPane import ChainPane
from db4e.Panes.P2PoolRemotePane import P2PoolRemotePane
from db4e.Panes.ResultsPane import ResultsPane
from db4e.Panes.RuntimeLogPane import RuntimeLogPane
from db4e.Panes.TUILogPane import TUILogPane
from db4e.Panes.UptimePane import UptimePane
from db4e.Panes.WelcomePane import WelcomePane
from db4e.Panes.XMRigHashratesPane import XMRigHashratesPane
from db4e.Panes.XMRigPane import XMRigPane
from db4e.Panes.XMRigRemotePane import XMRigRemotePane

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DPane import DPane



REGISTRY = {
    DPane.CHAIN_ANALYTICS: (ChainHashratesPane, DLabel.CHAIN, DLabel.HASHRATES),
    DPane.DB4E: (Db4EPane, DLabel.DB4E_LONG, DLabel.DB4E),
    DPane.DONATIONS: (DonationsPane, DLabel.DONATIONS, DLabel.DONATIONS),
    DPane.INITIAL_SETUP: (InitialSetupPane, DLabel.DB4E_LONG, DLabel.INITIAL_SETUP),
    DPane.LOG_VIEW: (LogViewPane, DLabel.LOG, DLabel.LOG_VIEWER),
    DPane.MONEROD: (MoneroDPane, DLabel.MONEROD, DLabel.NEW),
    DPane.MONEROD_REMOTE: (MoneroDRemotePane, DLabel.MONEROD_REMOTE, DLabel.CONFIG),
    DPane.P2POOL: (P2PoolPane, DLabel.P2POOL, DLabel.NEW),
    DPane.P2POOL_HASHRATES: (P2PoolHashratesPane, DLabel.P2POOL, DLabel.HASHRATES),
    DPane.CHAIN: (ChainPane, DLabel.P2POOL_INTERNAL, DLabel.CONFIG),
    DPane.P2POOL_REMOTE: (P2PoolRemotePane, DLabel.P2POOL_REMOTE, DLabel.CONFIG),
    DPane.RESULTS: (ResultsPane, DLabel.DB4E_LONG, DLabel.RESULTS),
    DPane.RUNTIME_LOG: (RuntimeLogPane, DLabel.LOG, DLabel.RUNTIME_LOG),
    DPane.TUI_LOG: (TUILogPane, DLabel.LOG, DLabel.TUI_LOG),
    DPane.UPTIME: (UptimePane, DLabel.DB4E_LONG, DLabel.RUNTIME),
    DPane.WELCOME: (WelcomePane, DLabel.DB4E_LONG, DLabel.WELCOME),
    DPane.XMRIG: (XMRigPane, DLabel.XMRIG, DLabel.NEW),
    DPane.XMRIG_HASHRATES: (XMRigHashratesPane, DLabel.XMRIG, DLabel.HASHRATES),
    DPane.XMRIG_REMOTE: (XMRigRemotePane, DLabel.XMRIG, DLabel.HASHRATES),
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