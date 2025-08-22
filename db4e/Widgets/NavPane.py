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

from textual import work
from textual.widgets import Label, Tree
from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer

#from db4e.Messages.NavLeafSelected import NavLeafSelected
from db4e.Modules.Db4E import Db4E
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.MoneroDRemote import MoneroDRemote
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.XMRig import XMRig
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Constants.Fields import (
    TUI_LOG_FIELD, DB4E_FIELD, DONATIONS_FIELD, ERROR_FIELD, GOOD_FIELD,
    MONEROD_REMOTE_FIELD, P2POOL_REMOTE_FIELD, INITIAL_SETUP_PROCEED_FIELD,
    INSTANCE_FIELD, MONEROD_FIELD, NEW_FIELD, P2POOL_FIELD, GET_TUI_LOG_FIELD,
    ELEMENT_TYPE_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, INSTALL_MGR_FIELD,
    OPS_MGR_FIELD, SET_PANE_FIELD, GET_NEW_FIELD, GET_REC_FIELD,
    UNKNOWN_FIELD, NAME_FIELD, PANE_MGR_FIELD, WARN_FIELD, XMRIG_FIELD)
from db4e.Constants.Labels import (
    DB4E_LABEL, DEPLOYMENTS_LABEL, DONATIONS_LABEL, INITIAL_SETUP_LABEL,
    MONEROD_SHORT_LABEL, P2POOL_SHORT_LABEL, TUI_LOG_LABEL, XMRIG_SHORT_LABEL)
from db4e.Constants.Panes import (
    MONEROD_TYPE_PANE, P2POOL_TYPE_PANE, DONATIONS_PANE, XMRIG_PANE,
    TUI_LOG_PANE)
from db4e.Constants.Buttons import NEW_LABEL

# Icon dictionary keys
CORE = 'CORE'
DEPL = 'DEPL'
GIFT = 'GIFT'
LOG = 'LOG'
MON = 'MON'
NEW = 'NEW'
P2P = 'P2P'
SETUP = 'SETUP'
XMR = 'XMR'

ICON = {
    CORE: '📡 ',
    DEPL: '💻 ',
    GIFT: '🎉 ',
    LOG: '📚 ',
    MON: '🌿 ',
    NEW: '🔧 ',
    P2P: '🌊 ',
    SETUP: '⚙️ ',
    XMR: '⛏️  '
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
    field: str
    icon: str

    def __str__(self):
        return self.icon + self.label



class NavPane(Container):


    def __init__(self, depl_mgr: DeploymentMgr):
        super().__init__()
        self.depl_mgr = depl_mgr
        self.health_mgr = HealthMgr()
        self._initialized = False

        # Create the Deployments tree
        self.depls = Tree(ICON[DEPL] + DEPLOYMENTS_LABEL, id="tree_deployments")
        self.depls.guide_depth = 3
        self.depls.root.expand()

        # Setup the navpane cache so we don't hammer the DB
        self._cached_deployments = []
        self._cache_time = 0
        self._cache_ttl = 1  # seconds
        self._refresh_now = False


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


    def clear_cache(self):
        self._refresh_now = True
        self.refresh_nav_pane()


    def compose(self) -> ComposeResult:
        yield Vertical(ScrollableContainer(self.depls, id="navpane"))


    def get_cached_deployments(self):
        now = time.time()
        if self._refresh_now or now - self._cache_time > self._cache_ttl:
            self._cached_deployments = self.depl_mgr.get_deployments()
            for elem in self._cached_deployments:
                if type(elem) == XMRig:
                    elem.p2pool = self.depl_mgr.get_deployment_by_id(elem.parent())
                    elem.p2pool.monerod = self.depl_mgr.get_deployment_by_id(elem.p2pool.parent())
                elif type(elem) == P2Pool:
                    elem.monerod = self.depl_mgr.get_deployment_by_id(elem.parent())
                self.health_mgr.check(elem)  
            self._cache_time = now
            self._refresh_now = False
        
        return self._cached_deployments
    

    def is_initialized(self) -> bool:
        #print(f"NavPane:is_initialized(): {self._initialized}")
        return self._initialized
    

    async def on_mount(self) -> None:
        self.set_interval(2, self.clear_cache)        
    

    @work(exclusive=True)
    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children and event.node.parent:
            leaf_item: NavItem = event.node.data
            parent_item: NavItem = event.node.parent.data
            #print(f"NavPane:on_tree_node_selected(): leaf_item ({leaf_item}), parent_item ({parent_item})")

            # Initial Setup
            if INITIAL_SETUP_LABEL in leaf_item.label:
                #print(f"NavPane:on_tree_node_selected(): {INITIAL_SETUP_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: DB4E_FIELD,
                    TO_MODULE_FIELD: INSTALL_MGR_FIELD,
                    TO_METHOD_FIELD: INITIAL_SETUP_PROCEED_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # View/Update Db4E Core
            elif DB4E_LABEL in leaf_item.label:
                #print(f"NavPane:on_tree_node_selected(): {DB4E_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: DB4E_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: GET_REC_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New Monero (remote) deployment
            elif NEW_LABEL in leaf_item.label and MONEROD_SHORT_LABEL in parent_item.label:
                #print(f"NavPane:on_tree_node_selected(): {MONEROD_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                    NAME_FIELD: MONEROD_TYPE_PANE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New P2Pool (remote) deployment
            elif NEW_LABEL in leaf_item.label and P2POOL_SHORT_LABEL in parent_item.label:
                #print(f"NavPane:on_tree_node_selected(): {P2POOL_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: P2POOL_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                    NAME_FIELD: P2POOL_TYPE_PANE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New XMRig deployment
            elif NEW_LABEL in leaf_item.label and XMRIG_SHORT_LABEL in parent_item.label:
                #print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: GET_NEW_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            elif parent_item:

                # View/Update a Monero deployment
                if MONEROD_SHORT_LABEL in parent_item.label:
                    #print(f"NavPane:on_tree_node_selected(): {MONEROD_SHORT_LABEL}/{leaf_item.label}")
                    for depl in self.get_cached_deployments():
                        if type(depl) == Db4E:
                            continue

                        if depl.instance() == leaf_item.field:
                            monerod = depl
                            break

                    if monerod.remote():
                        form_data = {
                            ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item.field
                        }
                    else:
                        form_data = {
                            ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item.field
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a P2Pool deployment
                elif P2POOL_SHORT_LABEL in parent_item.label:
                    #print(f"NavPane:on_tree_node_selected(): {P2POOL_SHORT_LABEL}/{leaf_item.label}")
                    for depl in self.get_cached_deployments():
                        if type(depl) == Db4E:
                            continue

                        if depl.instance() == leaf_item.field:
                            p2pool = depl
                            break

                    if p2pool.remote():
                        form_data = {
                            ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item.field
                        }
                    else:
                        form_data = {
                            ELEMENT_TYPE_FIELD: P2POOL_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item.field
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a XMRig deployment
                elif XMRIG_SHORT_LABEL in parent_item.label:
                    #print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT_LABEL}/{leaf_item.label}")
                    form_data = {
                        ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                        TO_MODULE_FIELD: OPS_MGR_FIELD,
                        TO_METHOD_FIELD: GET_REC_FIELD,
                        INSTANCE_FIELD: leaf_item.field
                    }
                    self.post_message(Db4eMsg(self, form_data=form_data))

            # TUI Log
            elif TUI_LOG_LABEL in leaf_item.label:
                #print(f"NavPane:on_tree_node_selected(): {TUI_LOG_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: TUI_LOG_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: GET_TUI_LOG_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # Donations
            elif DONATIONS_LABEL in leaf_item.label:
                #print(f"NavPane:on_tree_node_selected(): {DONATIONS_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: DONATIONS_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))


            elif isinstance(leaf_item, NavItem) and isinstance(parent_item, NavItem):
                self.post_message(NavLeafSelected(
                    self,
                    parent=parent_item.field, 
                    leaf=leaf_item.field
                ))
                event.stop()

    def refresh_nav_pane(self) -> None:
        self.set_initialized()
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
        
        # Precompute <New> label
        new_leaf = NavItem(NEW_LABEL, NEW_FIELD, ICON[NEW])
        
        # Map element_types to service categories
        service_mappings = {
            MONEROD_FIELD: [MoneroD, MoneroDRemote],
            P2POOL_FIELD: [P2Pool, P2PoolRemote], 
            XMRIG_FIELD: [XMRig]
        }

        depls = self.get_cached_deployments()

        # Group deployments by service category
        grouped: Dict[str, List[dict]] = {field: [] for field, _, _ in self.services}
        for elem in depls:
            # Find which service category this element_type belongs to
            for service_field, element_types in service_mappings.items():
                if type(elem) in element_types:
                    grouped[service_field].append(elem)
                    break

        #print(f"NavPane:refresh_nav_pane(): grouped: {grouped}")

        for field, icon, label in self.services:
            service_item = NavItem(label, field, icon)
            parent = self.depls.root.add(str(service_item), data=service_item, expand=True)
            for elem in grouped.get(field, []):
                state = elem.status()
                instance = elem.instance()
                #print(f"NavPane:refresh_nav_pane(): elem: {elem}, state: {state}")
                instance_item = NavItem(instance, instance, STATE_ICON.get(state, ""))
                parent.add_leaf(str(instance_item), data=instance_item)        

            # Add <New> if valid (i.e., P2Pool must exist before XMRIG)
            if field != XMRIG_FIELD or grouped.get(P2POOL_FIELD):
                parent.add_leaf(str(new_leaf), data=new_leaf)
        
        # Add Log link
        log_item = NavItem(TUI_LOG_LABEL, TUI_LOG_FIELD, ICON[LOG])
        self.depls.root.add_leaf(str(log_item), data=log_item)


        # Add Donations link
        donate_item = NavItem(DONATIONS_LABEL, DONATIONS_FIELD, ICON[GIFT])
        self.depls.root.add_leaf(str(donate_item), data=donate_item)


    def set_initialized(self):
        if not self._initialized:  
            self._initialized = self.depl_mgr.is_initialized()
        return self._initialized

