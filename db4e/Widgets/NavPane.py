"""
db4e/Widgets/NavPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.reactive import reactive
from textual.widgets import Label, Tree
from textual.app import ComposeResult
from textual.containers import Container, Vertical

from db4e.Messages.NavLeafSelected import NavLeafSelected
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.ConfigMgr import Config
from db4e.Constants.Labels import (
    DB4E_LABEL, DEPLOYMENTS_LABEL, DONATIONS_LABEL, METRICS_LABEL, MONEROD_SHORT_LABEL,
    NEW_LABEL, P2POOL_SHORT_LABEL, XMRIG_SHORT_LABEL
)
from db4e.Constants.Fields import (
    INSTANCE_FIELD, MONEROD_FIELD, MONEROD_REMOTE_FIELD, P2POOL_FIELD, XMRIG_FIELD
)

class NavPane(Container):
    def __init__(self, initialized_flag: bool, config: Config, **kwargs):
        super().__init__(**kwargs)
        self._initialized = initialized_flag
        self.depl_mgr = DeploymentMgr(config)

        self.depls = Tree(DEPLOYMENTS_LABEL, id="tree_deployments")
        self.depls.root.add_leaf(DB4E_LABEL)
        self.depls.guide_depth = 3
        self.depls.root.expand()

        self.metrics = Tree(METRICS_LABEL, id="tree_metrics")
        self.metrics.root.expand()

        self.donations = Label(DONATIONS_LABEL, id="donations")

    def compose(self) -> ComposeResult:
        yield Vertical(self.depls, self.metrics, self.donations, id="navpane")

    async def on_mount(self) -> None:
        self.metrics.guide_depth = 3

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children:
            self.post_message(NavLeafSelected(
                self, parent=event.node.parent.label, leaf=event.node.label))
            event.stop()

    def refresh_nav_pane(self) -> None:
        if self._initialized:
            self.depls.root.remove_children()

            self.depls.root.add_leaf(DB4E_LABEL)
            monero_node = self.depls.root.add(MONEROD_SHORT_LABEL)
            p2pool_node = self.depls.root.add(P2POOL_SHORT_LABEL)
            xmrig_node = self.depls.root.add(XMRIG_SHORT_LABEL)
            self.depls.root.expand()

            m_depls = self.depl_mgr.get_deployments(MONEROD_FIELD)
            for instance in m_depls.keys():
                monero_node.add_leaf(instance)
            monero_node.add_leaf(NEW_LABEL)
            monero_node.expand()

    def set_initialized(self, value: bool) -> None:
        self._initialized = value

