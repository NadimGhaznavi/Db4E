"""
Widgets/NavPane.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

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
    INSTANCE_FIELD, MONEROD_FIELD, LOG_VIEWER_FIELD, P2POOL_FIELD, GET_TUI_LOG_FIELD,
    ELEMENT_TYPE_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, INSTALL_MGR_FIELD,
    OPS_MGR_FIELD, SET_PANE_FIELD, GET_NEW_FIELD, GET_REC_FIELD,
    UNKNOWN_FIELD, NAME_FIELD, PANE_MGR_FIELD, WARN_FIELD, XMRIG_FIELD)
from db4e.Constants.Labels import (
    DB4E_LABEL, DEPLOYMENTS_LABEL, DONATIONS_LABEL, INITIAL_SETUP_LABEL,
    MONEROD_SHORT_LABEL, P2POOL_SHORT_LABEL, TUI_LOG_LABEL, XMRIG_SHORT_LABEL,
    LOG_FILE_LABEL, METRICS_LABEL)
from db4e.Constants.Panes import (
    MONEROD_TYPE_PANE, P2POOL_TYPE_PANE, DONATIONS_PANE, XMRIG_PANE,
    TUI_LOG_PANE)
from db4e.Constants.Buttons import NEW_LABEL

# Icon dictionary keys
CORE = 'CORE'
DEPL = 'DEPL'
GIFT = 'GIFT'
LOG = 'LOG'
MET = 'MET'
MON = 'MON'
NEW = 'NEW'
P2P = 'P2P'
SETUP = 'SETUP'
XMR = 'XMR'

ICON = {
    CORE: '📡',
    DEPL: '💻',
    GIFT: '🎉',
    LOG: '📚',
    MET: '🔎',
    MON: '🌿',
    NEW: '🔧',
    P2P: '🌊',
    SETUP: '⚙️',
    XMR: '⛏️ '
}

STATE_ICON = {
    GOOD_FIELD: '🟢',
    WARN_FIELD: '🟡',
    ERROR_FIELD: '🔴',
    UNKNOWN_FIELD: '⚪',
}


class NavPane(Container):


    def __init__(self, ops_mgr: OpsMgr):
        super().__init__()
        self.ops_mgr = ops_mgr
        self.health_mgr = ops_mgr.health_mgr
        self._initialized = False

        # Deployments tree
        self.depls = Tree(f"{ICON[DEPL]} {DEPLOYMENTS_LABEL}")
        self.depls.guide_depth = 3
        self.depls.root.expand()

        # Metrics Tree
        self.metrics = Tree(f"{ICON[MET]} {METRICS_LABEL}")
        self.metrics.guide_depth = 3
        self.metrics.root.expand()

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


    def compose(self) -> ComposeResult:
        yield Vertical(
            ScrollableContainer(
                Vertical(
                    self.depls,
                    self.metrics,
                )
            ),
            id="nav_pane"
        )
                


    def is_initialized(self) -> bool:
        #print(f"NavPane:is_initialized(): {self._initialized}")
        return self._initialized
    

    async def on_mount(self) -> None:
        self.set_interval(2, self.refresh_nav_pane)        
    

    @work(exclusive=True)
    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children and event.node.parent:
            leaf_item = event.node.data
            parent_item = event.node.parent.data
            #print(f"NavPane:on_tree_node_selected(): leaf_item ({leaf_item}), parent_item ({parent_item})")

            # Initial Setup
            if leaf_item ==INITIAL_SETUP_LABEL:
                #print(f"NavPane:on_tree_node_selected(): {INITIAL_SETUP_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: DB4E_FIELD,
                    TO_MODULE_FIELD: INSTALL_MGR_FIELD,
                    TO_METHOD_FIELD: INITIAL_SETUP_PROCEED_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # View/Update Db4E Core
            elif leaf_item == DB4E_LABEL:
                #print(f"NavPane:on_tree_node_selected(): {DB4E_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: DB4E_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: GET_REC_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # TUI Log
            elif leaf_item == TUI_LOG_LABEL:
                #print(f"NavPane:on_tree_node_selected(): {TUI_LOG_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: TUI_LOG_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: GET_TUI_LOG_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # Donations
            elif leaf_item == DONATIONS_LABEL:
                #print(f"NavPane:on_tree_node_selected(): {DONATIONS_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: DONATIONS_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New Monero (remote) deployment
            elif leaf_item == NEW_LABEL and parent_item == MONEROD_SHORT_LABEL:
                #print(f"NavPane:on_tree_node_selected(): {MONEROD_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                    NAME_FIELD: MONEROD_TYPE_PANE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New P2Pool (remote) deployment
            elif leaf_item == NEW_LABEL and parent_item == P2POOL_SHORT_LABEL:
                #print(f"NavPane:on_tree_node_selected(): {P2POOL_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: P2POOL_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                    NAME_FIELD: P2POOL_TYPE_PANE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New XMRig deployment
            elif leaf_item == NEW_LABEL and parent_item == XMRIG_SHORT_LABEL:
                #print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: GET_NEW_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            elif parent_item:

                # View/Update a Monero deployment
                if parent_item == MONEROD_SHORT_LABEL:
                    #print(f"NavPane:on_tree_node_selected(): {MONEROD_SHORT_LABEL}/{leaf_item.label}")
                    monerod = self.ops_mgr.get_deployment(
                        elem_type=MONEROD_FIELD, instance=str(leaf_item))

                    if monerod.remote():
                        form_data = {
                            ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item
                        }
                    else:
                        form_data = {
                            ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a P2Pool deployment
                elif parent_item == P2POOL_SHORT_LABEL:
                    #print(f"NavPane:on_tree_node_selected(): {P2POOL_SHORT_LABEL}/{leaf_item.label}")
                    p2pool = self.ops_mgr.get_deployment(
                        elem_type=P2POOL_FIELD, instance=str(leaf_item))

                    if p2pool.remote():
                        form_data = {
                            ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item
                        }
                    else:
                        form_data = {
                            ELEMENT_TYPE_FIELD: P2POOL_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a XMRig deployment
                elif parent_item == XMRIG_SHORT_LABEL:
                    #print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT_LABEL}/{leaf_item.label}")
                    form_data = {
                        ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                        TO_MODULE_FIELD: OPS_MGR_FIELD,
                        TO_METHOD_FIELD: GET_REC_FIELD,
                        INSTANCE_FIELD: leaf_item
                    }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View Metrics
                elif event.node.parent.parent and event.node.parent.parent.parent:
                    if leaf_item == LOG_FILE_LABEL:
                        grand_parent_item = event.node.parent.parent.data
                        form_data = {
                            ELEMENT_TYPE_FIELD: grand_parent_item,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: LOG_VIEWER_FIELD,
                            INSTANCE_FIELD: parent_item
                        }
                        print(f"NavPane:on_tree_node_selected(): {form_data}")
                        self.post_message(Db4eMsg(self, form_data=form_data))
                        

    def refresh_nav_pane(self) -> None:
        self.set_initialized()
        self.depls.root.remove_children()
        self.metrics.root.remove_children()
        
        if not self.is_initialized():
            self.depls.root.add_leaf(
                f"{ICON[SETUP]} {INITIAL_SETUP_LABEL}", data=INITIAL_SETUP_LABEL)
            self.depls.root.add_leaf(
                f"{ICON[GIFT]} {DONATIONS_LABEL}", data=DONATIONS_LABEL)
            return
        
        self.depls.root.add_leaf(
            f"{ICON[CORE]} {DB4E_LABEL}", data=DB4E_LABEL)
                
        monerod_tree = self.depls.root.add(
            f"{ICON[MON]} {MONEROD_SHORT_LABEL}", data=MONEROD_SHORT_LABEL, expand=True)
        monerods_list = []
        for monerod in self.ops_mgr.get_monerods():
            #print(f"NavPane:refresh_nav_pane(): {monerod}")
            state = monerod.status()
            monerod_tree.add_leaf(
                f"{STATE_ICON[state]} {monerod.instance()}", data=monerod.instance())
            monerods_list.append(monerod)
        monerod_tree.add_leaf(f"{ICON[NEW]} {NEW_LABEL}", data=NEW_LABEL)

        p2pool_tree = self.depls.root.add(
            f"{ICON[P2P]} {P2POOL_SHORT_LABEL}", data=P2POOL_SHORT_LABEL, expand=True)
        p2pools_list = []
        for p2pool in self.ops_mgr.get_p2pools():
            #print(f"NavPane:refresh_nav_pane(): {p2pool}")
            state = p2pool.status()
            p2pool_tree.add_leaf(
                f"{STATE_ICON[state]} {p2pool.instance()}", data=p2pool.instance())
            p2pools_list.append(p2pool)
        p2pool_tree.add_leaf(f"{ICON[NEW]} {NEW_LABEL}", data=NEW_LABEL)

        xmrig_tree = self.depls.root.add(
            f"{ICON[XMR]} {XMRIG_SHORT_LABEL}", data=XMRIG_SHORT_LABEL, expand=True)
        xmrigs_list = []
        for xmrig in self.ops_mgr.get_xmrigs():
            state = xmrig.status()
            xmrig_tree.add_leaf(
                f"{STATE_ICON[state]} {xmrig.instance()}", data=xmrig.instance())
            xmrigs_list.append(xmrig)
        xmrig_tree.add_leaf(f"{ICON[NEW]} {NEW_LABEL}", data=NEW_LABEL)
        
        monerod_metrics = self.metrics.root.add(
            f"{ICON[MON]} {MONEROD_SHORT_LABEL}", data=MONEROD_SHORT_LABEL, expand=True)
        for monerod in monerods_list:
            if not monerod.remote():
                monerod_metrics.add(
                    f"{ICON[MON]} {monerod.instance()}", data=monerod.instance(), expand=True)

        p2pool_metrics = self.metrics.root.add(
            f"{ICON[P2P]} {P2POOL_SHORT_LABEL}", data=P2POOL_SHORT_LABEL, expand=True)
        for p2pool in p2pools_list:
            if not p2pool.remote():
                instance_branch = p2pool_metrics.add(
                    f"{ICON[P2P]} {p2pool.instance()}", data=p2pool.instance(), expand=True)
                instance_branch.add_leaf(f"{ICON[LOG]} {LOG_FILE_LABEL}", data=LOG_FILE_LABEL)

        xmrig_metrics = self.metrics.root.add(
            f"{ICON[XMR]} {XMRIG_SHORT_LABEL}", data=XMRIG_SHORT_LABEL, expand=True)
        for xmrig in xmrigs_list:
            instance_branch = xmrig_metrics.add(
                f"{ICON[XMR]} {xmrig.instance()}", data=xmrig.instance(), expand=True)
            instance_branch.add_leaf(f"{ICON[LOG]} {LOG_FILE_LABEL}", data=LOG_FILE_LABEL)

        # Add Log link
        self.metrics.root.add_leaf(f"{ICON[LOG]} {TUI_LOG_LABEL}", data=TUI_LOG_LABEL)

        # Add Donations link
        self.metrics.root.add_leaf(f"{ICON[GIFT]} {DONATIONS_LABEL}", data=DONATIONS_LABEL)


    def set_initialized(self):
        if not self._initialized:  
            self._initialized = self.ops_mgr.depl_mgr.is_initialized()
        return self._initialized

