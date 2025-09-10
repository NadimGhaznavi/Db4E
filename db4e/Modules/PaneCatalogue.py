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
from db4e.Constants.Panes import Pane


REGISTRY = {
    Pane.DB4E.value: (Db4EPane, DLabel.DB4E_LONG, DLabel.DB4E),
    Pane.DONATIONS.value: (DonationsPane, DLabel.DONATIONS, DLabel.DONATIONS),
    Pane.INITIAL_SETUP.value: (InitialSetupPane, DLabel.DB4E_LONG, DLabel.INITIAL_SETUP),
    Pane.LOG_VIEW.value: (LogViewPane, DLabel.LOG, DLabel.LOG_VIEWER),
    Pane.MONEROD_TYPE.value: (MoneroDTypePane, DLabel.MONEROD, DLabel.NEW),
    Pane.MONEROD.value: (MoneroDPane, DLabel.MONEROD, DLabel.NEW),
    Pane.MONEROD_REMOTE.value: (MoneroDRemotePane, DLabel.MONEROD_REMOTE, DLabel.CONFIG),
    Pane.P2POOL_TYPE.value: (P2PoolTypePane, DLabel.P2POOL, DLabel.NEW),
    Pane.P2POOL.value: (P2PoolPane, DLabel.P2POOL, DLabel.NEW),
    Pane.P2POOL_REMOTE.value: (P2PoolRemotePane, DLabel.P2POOL_REMOTE, DLabel.CONFIG),
    Pane.PLOT_VIEW.value: (PlotViewPane, DLabel.ANALYTICS, DLabel.PLOT),
    Pane.XMRIG.value: (XMRigPane, DLabel.XMRIG, DLabel.NEW),
    Pane.RESULTS.value: (ResultsPane, DLabel.DB4E_LONG, DLabel.RESULTS),
    Pane.TUI_LOG.value: (TUILogPane, DLabel.LOG, DLabel.TUI_LOG),
    Pane.WELCOME.value: (WelcomePane, DLabel.DB4E_LONG, DLabel.WELCOME),
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