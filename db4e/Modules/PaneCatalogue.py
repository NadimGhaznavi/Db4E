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
from db4e.Constants.Labels import (
    DB4E_LABEL, DB4E_LONG_LABEL, INITIAL_SETUP_LABEL, RESULTS_LABEL, WELCOME_LABEL
)
from db4e.Constants.Panes import DB4E_PANE, INITIAL_SETUP_PANE, RESULTS_PANE, WELCOME_PANE


REGISTRY = {
    DB4E_PANE: (Db4E, DB4E_LONG_LABEL, DB4E_LABEL),
    INITIAL_SETUP_PANE: (InitialSetup, DB4E_LONG_LABEL, INITIAL_SETUP_LABEL),
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