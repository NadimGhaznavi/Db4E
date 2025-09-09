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
from db4e.Panes.LogViewPane import LogViewPane
from db4e.Panes.MoneroDPane import MoneroDPane
from db4e.Panes.MoneroDRemotePane import MoneroDRemotePane
from db4e.Panes.MoneroDTypePane import MoneroDTypePane
from db4e.Panes.P2PoolPane import P2PoolPane
from db4e.Panes.P2PoolRemotePane import P2PoolRemotePane
from db4e.Panes.P2PoolTypePane import P2PoolTypePane
from db4e.Panes.PlotViewPane import PlotViewPane
from db4e.Panes.ResultsPane import ResultsPane
from db4e.Panes.TUILogPane import TUILogPane
from db4e.Panes.WelcomePane import WelcomePane
from db4e.Panes.XMRigPane import XMRigPane


from db4e.Constants.Labels import DLabel
from db4e.Constants.Panes import (
    DB4E_PANE, DONATIONS_PANE, INITIAL_SETUP_PANE, MONEROD_REMOTE_PANE, 
    MONEROD_PANE, MONEROD_TYPE_PANE, P2POOL_PANE, P2POOL_TYPE_PANE, 
    P2POOL_REMOTE_PANE, RESULTS_PANE, WELCOME_PANE, XMRIG_PANE, TUI_LOG_PANE,
    LOG_VIEW_PANE, PLOT_VIEW_PANE, LOG_VIEW_PANE)


REGISTRY = {
    DB4E_PANE: (Db4EPane, DLabel.DB4E_LONG, DLabel.DB4E),
    DONATIONS_PANE: (DonationsPane, DLabel.DONATIONS, DLabel.DONATIONS),
    INITIAL_SETUP_PANE: (InitialSetupPane, DLabel.DB4E_LONG, DLabel.INITIAL_SETUP),
    LOG_VIEW_PANE: (LogViewPane, DLabel.LOG, DLabel.LOG_VIEWER),
    MONEROD_TYPE_PANE: (MoneroDTypePane, DLabel.MONEROD, DLabel.NEW),
    MONEROD_PANE: (MoneroDPane, DLabel.MONEROD, DLabel.NEW),
    MONEROD_REMOTE_PANE: (MoneroDRemotePane, DLabel.MONEROD_REMOTE, DLabel.CONFIG),
    P2POOL_TYPE_PANE: (P2PoolTypePane, DLabel.P2POOL, DLabel.NEW),
    P2POOL_PANE: (P2PoolPane, DLabel.P2POOL, DLabel.NEW),
    P2POOL_REMOTE_PANE: (P2PoolRemotePane, DLabel.P2POOL_REMOTE, DLabel.CONFIG),
    PLOT_VIEW_PANE: (PlotViewPane, DLabel.ANALYTICS, DLabel.PLOT),
    XMRIG_PANE: (XMRigPane, DLabel.XMRIG, DLabel.NEW),
    RESULTS_PANE: (ResultsPane, DLabel.DB4E_LONG, DLabel.RESULTS),
    TUI_LOG_PANE: (TUILogPane, DLabel.LOG, DLabel.TUI_LOG),
    WELCOME_PANE: (WelcomePane, DLabel.DB4E_LONG, DLabel.WELCOME),
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