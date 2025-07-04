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
from db4e.Panes.InstallResults import InstallResults
from db4e.Panes.Db4E import Db4E


REGISTRY = {
    "Db4E": (Db4E, "Database 4 Everything", "Db4E Core"),
    "InitialSetup": (InitialSetup, "Database 4 Everything", "Initial Setup"),
    "InstallResults": (InstallResults, "Database 4 Everything", "Install Results"),
    "Welcome": (Welcome, "Database 4 Everything", "Welcome"),
}

class PaneCatalogue:

    def __init__(self):
        self.registry = REGISTRY

    def get_pane(self, pane_name: str, pane_data=None) -> Container:
        pane_class, _, _ = self.registry[pane_name]
        print(f"PaneCatalogue:get_pane(): {pane_name}")
        return pane_class(id=pane_name, data=pane_data) if pane_data else pane_class(id=pane_name)

    def get_metadata(self, pane_name: str) -> tuple[str, str]:
        _, component, msg = self.registry.get(pane_name, (None, "", ""))
        return component, msg