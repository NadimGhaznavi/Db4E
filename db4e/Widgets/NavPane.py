"""
db4e/Widgets/NavPane.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

from textual.widgets import Label, Tree
from textual.app import ComposeResult
from textual.containers import Container, Vertical

class NavPane(Container):
    def __init__(self, initialized: bool, **kwargs):
        self.initialized = initialized
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        depls: Tree[str] = Tree("Deployments", id="tree_deployments")
        depls.root.add_leaf("db4e core")
        depls.guide_depth = 3
        depls.root.expand()
        metrics: Tree[str] = Tree("Metrics", id="tree_metrics")
        metrics.guide_depth = 3
        metrics.root.expand()
        donations = Label("Donations", id="donations")
        if not self.initialized:
            yield Vertical(depls, metrics, donations, id="navbar")
            return
        
        # Detployments 
        monero_depls = depls.root.add("Monero")
        monero_depls.add_leaf("New")
        p2pool_depls = depls.root.add("P2Pool")
        p2pool_depls.add_leaf("New")
        xmrig_depls = depls.root.add("XMRig")
        xmrig_depls.add_leaf("New")

        # Metrics
        metrics.root.add_leaf("db4e core")
        metrics.root.add_leaf("Monero")
        metrics.root.add_leaf("P2Pool")
        metrics.root.add_leaf("XMRig")
        
        yield Vertical(depls, metrics, donations, id="navbar")