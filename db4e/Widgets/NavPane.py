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


class NavPane(Container):


    def __init__(self, ops_mgr: OpsMgr):
        super().__init__()
        self.ops_mgr = ops_mgr
        self.health_mgr = ops_mgr.health_mgr
        self._initialized = False

        # Create the Deployments tree
        self.depls = Tree(ICON[DEPL] + DEPLOYMENTS_LABEL, id="tree_deployments")
        self.depls.guide_depth = 3
        self.depls.root.expand()

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
        yield Vertical(ScrollableContainer(self.depls, id="navpane"))


    def is_initialized(self) -> bool:
        #print(f"NavPane:is_initialized(): {self._initialized}")
        return self._initialized
    

    async def on_mount(self) -> None:
        self.set_interval(2, self.refresh_nav_pane)        
    

    @work(exclusive=True)
    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children and event.node.parent:
            leaf_item = event.node
            parent_item = event.node.parent
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
                    monerod = self.ops_mgr.get_deployment(
                        elem_type=MONEROD_FIELD, instance=str(leaf_item.label)[2:])

                    if monerod.remote():
                        form_data = {
                            ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: str(leaf_item.label)[2:]
                        }
                    else:
                        form_data = {
                            ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: str(leaf_item.label)[2:]
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a P2Pool deployment
                elif P2POOL_SHORT_LABEL in parent_item.label:
                    #print(f"NavPane:on_tree_node_selected(): {P2POOL_SHORT_LABEL}/{leaf_item.label}")
                    p2pool = self.ops_mgr.get_deployment(
                        elem_type=P2POOL_FIELD, instance=str(leaf_item.label)[2:])

                    if p2pool.remote():
                        form_data = {
                            ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: str(leaf_item.label)[2:]
                        }
                    else:
                        form_data = {
                            ELEMENT_TYPE_FIELD: P2POOL_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: str(leaf_item.label)[2:]
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a XMRig deployment
                elif XMRIG_SHORT_LABEL in parent_item.label:
                    #print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT_LABEL}/{leaf_item.label}")
                    form_data = {
                        ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                        TO_MODULE_FIELD: OPS_MGR_FIELD,
                        TO_METHOD_FIELD: GET_REC_FIELD,
                        INSTANCE_FIELD: str(leaf_item.label)[2:]
                    }
                    self.post_message(Db4eMsg(self, form_data=form_data))


    def refresh_nav_pane(self) -> None:
        self.set_initialized()
        self.depls.root.remove_children()
        
        if not self.is_initialized():
            self.depls.root.add_leaf(ICON[SETUP] + INITIAL_SETUP_LABEL)
            self.depls.root.add_leaf(ICON[GIFT] + DONATIONS_LABEL)
            return
        
        self.depls.root.add_leaf(ICON[CORE] + DB4E_LABEL)
        
        # Precompute <New> label
        new_leaf = ICON[NEW] + NEW_LABEL
        
        monerod_tree = self.depls.root.add(ICON[MON] + MONEROD_SHORT_LABEL, expand=True)
        for monerod in self.ops_mgr.get_monerods():
            #print(f"NavPane:refresh_nav_pane(): {monerod}")
            state = monerod.status()
            monerod_tree.add_leaf(STATE_ICON.get(state, "") + monerod.instance())
        monerod_tree.add_leaf(new_leaf)

        p2pool_tree = self.depls.root.add(ICON[P2P] + P2POOL_SHORT_LABEL, expand=True)
        for p2pool in self.ops_mgr.get_p2pools():
            #print(f"NavPane:refresh_nav_pane(): {p2pool}")
            state = p2pool.status()
            p2pool_tree.add_leaf(STATE_ICON.get(state, "") + p2pool.instance())
        p2pool_tree.add_leaf(new_leaf)

        xmrig_tree = self.depls.root.add(ICON[XMR] + XMRIG_SHORT_LABEL, expand=True)
        for xmrig in self.ops_mgr.get_xmrigs():
            state = xmrig.status()
            xmrig_tree.add_leaf(STATE_ICON.get(state, "") + xmrig.instance())
        xmrig_tree.add_leaf(new_leaf)
        
        # Add Log link
        self.depls.root.add_leaf(ICON[LOG] + TUI_LOG_LABEL)

        # Add Donations link
        self.depls.root.add_leaf(ICON[GIFT] + DONATIONS_LABEL)


    def set_initialized(self):
        if not self._initialized:  
            self._initialized = self.ops_mgr.depl_mgr.is_initialized()
        return self._initialized

