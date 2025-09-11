"""
db4e/Modules/PaneCatalogue.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container

from db4e.Panes import (
    Db4EPane, DonationsPane, InitialSetupPane, LogViewPane, MoneroDPane, 
    MoneroDRemotePane, MoneroDTypePane, P2PoolPane, P2PoolRemotePane, 
    P2PoolTypePane, PlotViewPane, ResultsPane, TUILogPane, WelcomePane, 
    XMRigPane
)
from db4e.Constants import DLabel, DPane



REGISTRY = {
    DPane.DB4E: (Db4EPane, DLabel.DB4E_LONG, DLabel.DB4E),
    DPane.DONATIONS: (DonationsPane, DLabel.DONATIONS, DLabel.DONATIONS),
    DPane.INITIAL_SETUP: (InitialSetupPane, DLabel.DB4E_LONG, DLabel.INITIAL_SETUP),
    DPane.LOG_VIEW: (LogViewPane, DLabel.LOG, DLabel.LOG_VIEWER),
    DPane.MONEROD_TYPE: (MoneroDTypePane, DLabel.MONEROD, DLabel.NEW),
    DPane.MONEROD: (MoneroDPane, DLabel.MONEROD, DLabel.NEW),
    DPane.MONEROD_REMOTE: (MoneroDRemotePane, DLabel.MONEROD_REMOTE, DLabel.CONFIG),
    DPane.P2POOL_TYPE: (P2PoolTypePane, DLabel.P2POOL, DLabel.NEW),
    DPane.P2POOL: (P2PoolPane, DLabel.P2POOL, DLabel.NEW),
    DPane.P2POOL_REMOTE: (P2PoolRemotePane, DLabel.P2POOL_REMOTE, DLabel.CONFIG),
    DPane.PLOT_VIEW: (PlotViewPane, DLabel.ANALYTICS, DLabel.PLOT),
    DPane.XMRIG: (XMRigPane, DLabel.XMRIG, DLabel.NEW),
    DPane.RESULTS: (ResultsPane, DLabel.DB4E_LONG, DLabel.RESULTS),
    DPane.TUI_LOG: (TUILogPane, DLabel.LOG, DLabel.TUI_LOG),
    DPane.WELCOME: (WelcomePane, DLabel.DB4E_LONG, DLabel.WELCOME),
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