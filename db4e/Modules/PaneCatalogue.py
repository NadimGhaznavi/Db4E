"""
db4e/Modules/PaneCatalogue.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container

from db4e.Panes.Welcome import Welcome
from db4e.Panes.InitialSetup import InitialSetup
from db4e.Panes.Results import Results
from db4e.Panes.Db4E import Db4E
from db4e.Panes.MonerodRemote import MonerodRemote
from db4e.Panes.NewMonerodType import NewMonerodType
from db4e.Panes.NewMonerod import NewMonerod
from db4e.Panes.P2PoolRemote import P2PoolRemote
from db4e.Panes.NewP2PoolType import NewP2PoolType
from db4e.Panes.NewP2Pool import NewP2Pool


from db4e.Constants.Labels import (
    CONFIG_LABEL, DB4E_LABEL, DB4E_LONG_LABEL, INITIAL_SETUP_LABEL, NEW_LABEL, 
    MONEROD_LABEL, MONEROD_REMOTE_LABEL, P2POOL_LABEL, P2POOL_REMOTE_LABEL, 
    RESULTS_LABEL, WELCOME_LABEL
)
from db4e.Constants.Panes import (
    DB4E_PANE, INITIAL_SETUP_PANE, MONEROD_REMOTE_PANE, NEW_MONEROD_PANE, 
    NEW_MONEROD_TYPE_PANE, NEW_P2POOL_PANE, NEW_P2POOL_TYPE_PANE, 
    P2POOL_REMOTE_PANE, RESULTS_PANE, WELCOME_PANE
)

REGISTRY = {
    DB4E_PANE: (Db4E, DB4E_LONG_LABEL, DB4E_LABEL),
    INITIAL_SETUP_PANE: (InitialSetup, DB4E_LONG_LABEL, INITIAL_SETUP_LABEL),
    MONEROD_REMOTE_PANE: (MonerodRemote, MONEROD_REMOTE_LABEL, CONFIG_LABEL),
    P2POOL_REMOTE_PANE: (P2PoolRemote, P2POOL_REMOTE_LABEL, CONFIG_LABEL),
    NEW_MONEROD_TYPE_PANE: (NewMonerodType, NEW_LABEL, MONEROD_LABEL),
    NEW_MONEROD_PANE: (NewMonerod, NEW_LABEL, MONEROD_LABEL),
    NEW_P2POOL_TYPE_PANE: (NewP2PoolType, NEW_LABEL, P2POOL_LABEL),
    NEW_P2POOL_PANE: (NewP2Pool, NEW_LABEL, P2POOL_LABEL),    
    RESULTS_PANE: (Results, DB4E_LONG_LABEL, RESULTS_LABEL),
    WELCOME_PANE: (Welcome, DB4E_LONG_LABEL, WELCOME_LABEL),
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