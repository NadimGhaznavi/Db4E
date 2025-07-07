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

from db4e.Messages.NavLeafSelected import NavLeafSelected

class NavPane(Container):
    def __init__(self, initialized: bool, **kwargs):
        super().__init__(**kwargs)
        self.initialized = initialized
        self.depls = Tree("Deployments", id="tree_deployments")
        self.metrics = Tree("Metrics", id="tree_metrics")

    def compose(self) -> ComposeResult:
        self.depls.root.add_leaf("Db4E Core")
        self.depls.guide_depth = 3
        self.depls.root.expand()
        self.metrics.guide_depth = 3
        self.metrics.root.expand()
        donations = Label("Donations", id="donations")
        if not self.initialized:
            yield Vertical(self.depls, self.metrics, donations, id="navpane")
            return
        
        # Detployments 
        monero_depls = self.depls.root.add("Monero")
        monero_depls.add_leaf("New")
        p2pool_depls = self.depls.root.add("P2Pool")
        p2pool_depls.add_leaf("New")
        xmrig_depls = self.depls.root.add("XMRig")
        xmrig_depls.add_leaf("New")

        # Metrics
        self.metrics.root.add_leaf("db4e core")
        self.metrics.root.add_leaf("Monero")
        self.metrics.root.add_leaf("P2Pool")
        self.metrics.root.add_leaf("XMRig")
        
        yield Vertical(self.depls, self.metrics, donations, id="navpane")

    def refresh_nav_pane(self):
        # Refresh and resize the NavPane
        self.refresh(layout=True)

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children:
            self.post_message(NavLeafSelected(
                self, parent=event.node.parent.label, leaf=event.node.label))
            event.stop()    