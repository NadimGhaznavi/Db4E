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
    DB4E_FIELD, MONEROD_FIELD, P2POOL_FIELD, USER_WALLET_FIELD, 
    VENDOR_DIR_FIELD
)

class NavPane(Container):
    def __init__(self, config: Config):
        super().__init__()
        self.depl_mgr = DeploymentMgr(config)
        self._initialized = False

        self.depls = Tree(DEPLOYMENTS_LABEL, id="tree_deployments")
        self.depls.root.add_leaf(DB4E_LABEL)
        self.depls.guide_depth = 3
        self.depls.root.expand()

        #self.metrics = Tree(METRICS_LABEL, id="tree_metrics")
        #self.metrics.root.expand()
        #self.metrics.guide_depth = 3
        self.donations = Label(DONATIONS_LABEL, id="donations")
        self.refresh_nav_pane()

    def check_initialized(self):
        db4e_rec = self.depl_mgr.get_deployment(DB4E_FIELD)
        if db4e_rec and db4e_rec.get(VENDOR_DIR_FIELD) and db4e_rec.get(USER_WALLET_FIELD):
            self.set_initialized(True)
        else:
            self.set_initialized(False)

    def compose(self) -> ComposeResult:
        #yield Vertical(self.depls, self.metrics, self.donations, id="navpane")
        yield Vertical(self.depls, self.donations, id="navpane")

    def is_initialized(self) -> bool:
        return self._initialized

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children:
            self.post_message(NavLeafSelected(
                self, parent=event.node.parent.label, leaf=event.node.label))
            event.stop()

    def refresh_nav_pane(self) -> None:
        if not self.is_initialized():
            self.check_initialized()

        if self.is_initialized():
            # Rebuild the NavPane trees
            self.depls.root.remove_children()
            self.depls.root.add_leaf(DB4E_LABEL)
            self.depls.root.expand()

            # The Monero tree
            monero_node = self.depls.root.add(MONEROD_SHORT_LABEL)
            instances = self.depl_mgr.get_deployment_instances(MONEROD_FIELD)
            for instance in instances:
                monero_node.add_leaf(instance)
            monero_node.add_leaf(NEW_LABEL)
            monero_node.expand()

            p2pool_node = self.depls.root.add(P2POOL_SHORT_LABEL)
            instances = self.depl_mgr.get_deployment_instances(P2POOL_FIELD)
            for instance in instances:
                p2pool_node.add_leaf(instance)
            # Only allow P2Pool deployments if a Monero daemon deployment exists
            if len(monero_node.children) > 1:
                p2pool_node.add_leaf(NEW_LABEL)
            p2pool_node.expand()

            # Only display XMRig if a P2Pool deployment exists
            xmrig_node = self.depls.root.add(XMRIG_SHORT_LABEL)
            # Only allow XMRig deployments if a P2Pool deployment exists
            if len(p2pool_node.children) > 1:
                xmrig_node.add_leaf(NEW_LABEL)

    def set_initialized(self, value: bool) -> None:
        self._initialized = value

