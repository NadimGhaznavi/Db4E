"""
Widgets/NavPane.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple
import time

from textual.reactive import reactive
from textual.widgets import Label, Tree
from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer

from db4e.Messages.NavLeafSelected import NavLeafSelected
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.ConfigMgr import Config
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DB4E_FIELD, DONATIONS_FIELD, ERROR_FIELD, GOOD_FIELD,
    DEPLOYMENTS_FIELD,
    INSTANCE_FIELD, MONEROD_FIELD, NEW_FIELD, P2POOL_FIELD, STATUS_FIELD,
    UNKNOWN_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD, WARN_FIELD, XMRIG_FIELD)
from db4e.Constants.Labels import (
    DB4E_LABEL, DEPLOYMENTS_LABEL, DONATIONS_LABEL, INITIAL_SETUP_LABEL,
    MONEROD_SHORT_LABEL, NEW_LABEL, P2POOL_SHORT_LABEL, XMRIG_SHORT_LABEL)

# Icon dictionary keys
CORE = 'CORE'
DEPL = 'DEPL'
GIFT = 'GIFT'
MON = 'MON'
NEW = 'NEW'
P2P = 'P2P'
SETUP = 'SETUP'
XMR = 'XMR'

ICON = {
    CORE: '📡 ',
    DEPL: '💻 ',
    GIFT: '🎉 ',
    MON: '🌿 ',
    NEW: '🔧 ',
    P2P: '🌊 ',
    SETUP: '⚙️ ',
    XMR: '⛏️'
}

STATE_ICON = {
    GOOD_FIELD: '🟢 ',
    WARN_FIELD: '🟡 ',
    ERROR_FIELD: '🔴 ',
    UNKNOWN_FIELD: '⚪ ',
}

@dataclass
class NavItem:
    label: str
    route_id: str
    icon: str

    def __str__(self):
        return self.icon + self.label

    @property
    def value(self) -> str:
        return self.route_id

class NavPane(Container):

    def __init__(self, config: Config, ops_mgr: OpsMgr):
        super().__init__()
        self.ops_mgr = ops_mgr
        self.health_mgr = HealthMgr()
        self._initialized = False

        # Create the Deployments tree
        self.depls = Tree(ICON[DEPL] + DEPLOYMENTS_LABEL, id="tree_deployments")
        self.depls.guide_depth = 2
        self.depls.root.expand()

        # Setup the navpane cache so we don't hammer the DB
        self._cached_deployments = []
        self._cache_time = 0
        self._cache_ttl = 10  # seconds

        # Current state data from Mongo
        self.monerod_recs = None
        self.p2pool_recs = None
        self.xmrig_recs = None

        # Configure services with their health check handlers
        self.services = [
            (MONEROD_FIELD, ICON[MON], MONEROD_SHORT_LABEL),
            (P2POOL_FIELD, ICON[P2P], P2POOL_SHORT_LABEL),
            (XMRIG_FIELD, ICON[XMR], XMRIG_SHORT_LABEL),
        ]

        self.refresh_nav_pane()

    def check_initialized(self):
        rec = self.ops_mgr.get_deployment(elem_type=DB4E_FIELD)
        self._initialized = bool(rec and rec.get(VENDOR_DIR_FIELD) and \
                                 rec.get(USER_WALLET_FIELD))
        return self._initialized

    def compose(self) -> ComposeResult:
        yield Vertical(ScrollableContainer(self.depls, id="navpane"))

    def flush_cache(self):
        self._cached_deployments = self.ops_mgr.get_deployments()
        self._cache_time = time.time()
        self.refresh_nav_pane()

    def get_cached_deployments(self):
        now = time.time()
        if now - self._cache_time > self._cache_ttl:
            self._cached_deployments = self.ops_mgr.get_deployments()
            self._cache_time = now
        return self._cached_deployments
    
    def is_initialized(self) -> bool:
        #print(f"NavPane:is_initialized(): {self._initialized}")
        return self._initialized

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children and event.node.parent:
            leaf_item: NavItem = event.node.data
            parent_item: NavItem = event.node.parent.data
            print(f"NavPane:on_tree_node_selected(): leaf_item {leaf_item}, parent_item {parent_item}")

            if parent_item is None:
                self.post_message(NavLeafSelected(
                    self,
                    parent=DEPLOYMENTS_FIELD,  # the route, not the label
                    leaf=leaf_item.route_id
                ))
            elif isinstance(leaf_item, NavItem) and isinstance(parent_item, NavItem):
                self.post_message(NavLeafSelected(
                    self,
                    parent=parent_item.route_id,  # the route, not the label
                    leaf=leaf_item.route_id       # the route, not the label
                ))
                event.stop()

    def refresh_nav_pane(self) -> None:
        self.check_initialized()
        self.depls.root.remove_children()

        # Db4E Core root node
        core_item = NavItem(DB4E_LABEL, DB4E_FIELD, ICON[CORE])
        setup_item = NavItem(INITIAL_SETUP_LABEL, DB4E_FIELD, ICON[SETUP])

        if not self.is_initialized():
            # Add Donations link
            donate_item = NavItem(DONATIONS_LABEL, DONATIONS_FIELD, ICON[GIFT])
            self.depls.root.add_leaf(str(setup_item), data=setup_item)
            self.depls.root.add_leaf(str(donate_item), data=donate_item)
            return

        self.depls.root.add_leaf(str(core_item), data=core_item)
        all_recs = self.get_cached_deployments()  # Cached call
        #print(f"NavPane:refresh_nav_pane(): all_recs {all_recs}")

        # Precompute <New> label
        new_leaf = NavItem(NEW_LABEL, NEW_FIELD, ICON[NEW])

        # Group deployments by component
        grouped: Dict[str, List[dict]] = {field: [] for field, _, _ in self.services}
        for rec in all_recs:
            grouped.setdefault(rec.get(COMPONENT_FIELD), []).append(rec)

        for field, icon, label in self.services:
            service_item = NavItem(label, field, icon)
            parent = self.depls.root.add(str(service_item), data=service_item, expand=True)

            for rec in grouped.get(field, []):
                instance = rec.get(INSTANCE_FIELD)
                state = rec.get(STATUS_FIELD)
                instance_item = NavItem(instance, instance, STATE_ICON.get(state, ""))
                parent.add_leaf(str(instance_item), data=instance_item)

            # Add <New> if valid (i.e., P2Pool must exist before XMRIG)
            if field != XMRIG_FIELD or grouped.get(P2POOL_FIELD):
                parent.add_leaf(str(new_leaf), data=new_leaf)

        # Add Donations link
        donate_item = NavItem(DONATIONS_LABEL, DONATIONS_FIELD, ICON[GIFT])
        self.depls.root.add_leaf(str(donate_item), data=donate_item)
