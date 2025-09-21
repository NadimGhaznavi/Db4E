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

from db4e.Modules.DbMgr import DbMgr
from db4e.Modules.HealthCache import HealthCache
from db4e.Modules.OpsMgr import OpsMgr

from db4e.Messages.Db4eMsg import Db4eMsg

from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DModule import DModule
from db4e.Constants.DPane import DPane
from db4e.Constants.DStatus import DStatus

# Icon dictionary keys
BLOCK = 'BLOCK'
CORE = 'CORE'
CHAIN = 'CHAIN'
DEPL = 'DEPL'
GIFT = 'GIFT'
HASH = 'HASH'
LOG = 'LOG'
MAIN = 'MAIN'
MET = 'MET'
MINERS = 'MINERS'
MINI = 'MINI'
NANO = 'NANO'
MON = 'MON'
NEW = 'NEW'
P2P = 'P2P'
SETUP = 'SETUP'
XMR = 'XMR'

ICON = {
    BLOCK: '🧱',
    CHAIN: '⛓️',
    CORE: '📡',
    DEPL: '💻',
    GIFT: '🎉',
    HASH: '📉',
    LOG: '📚',
    MAIN: '🌕',
    MET: '🔎',
    MINERS: '👷',
    MINI: '🌗',
    NANO: '🌘',
    MON: '🌿',
    NEW: '🔧',
    P2P: '🌊',
    SETUP: '⚙️',
    XMR: '⛏️ '
}

STATE_ICON = {
    DStatus.GOOD: '🟢',
    DStatus.WARN: '🟡',
    DStatus.ERROR: '🔴',
    DStatus.UNKNOWN: '🕓',
}


class NavPane(Container):


    def __init__(self, health_cache: HealthCache, ops_mgr: OpsMgr):
        super().__init__()
        self.ops_mgr = ops_mgr
        self.health_cache = health_cache
        self._initialized = False

        # Deployments tree
        self.depls = Tree(f"{ICON[DEPL]} {DLabel.DEPLOYMENTS}")
        self.depls.guide_depth = 3
        self.depls.root.expand()

        self.depls_branches_added, self.initial_branches_added = False, False
        
        self.depls_branch_state = {
            DElem.MONEROD: {},
            DElem.P2POOL: {},
            DElem.XMRIG: {}
        }

        self.refresh_nav_pane()


    def compose(self) -> ComposeResult:
        yield Vertical(
            ScrollableContainer(
                Vertical(
                    self.depls,
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
            leaf_data = event.node.data
            parent_data = event.node.parent.data
            #print(f"NavPane:on_tree_node_selected(): leaf_item ({leaf_data}), parent_item ({parent_data})")

            # Initial Setup
            if leaf_data == DLabel.INITIAL_SETUP:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.DB4E,
                    DField.TO_MODULE: DModule.INSTALL_MGR,
                    DField.TO_METHOD: DMethod.INITIAL_SETUP_PROCEED,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # View/Update Db4E Core
            elif leaf_data == DLabel.DB4E:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.DB4E,
                    DField.TO_MODULE: DModule.OPS_MGR,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # TUI Log
            elif leaf_data == DLabel.TUI_LOG:
                form_data = {
                    DField.ELEMENT_TYPE: DField.TUI_LOG,
                    DField.TO_MODULE: DModule.OPS_MGR,
                    DField.TO_METHOD: DMethod.GET_TUI_LOG,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # Donations
            elif leaf_data == DLabel.DONATIONS:
                form_data = {
                    DField.ELEMENT_TYPE: DField.DONATIONS,
                    DField.TO_MODULE: DModule.OPS_MGR,
                    DField.TO_METHOD: DMethod.SET_DONATIONS,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))


            # New Monero (remote) deployment
            elif leaf_data == DLabel.NEW and parent_data == DLabel.MONEROD_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.MONEROD,
                    DField.TO_MODULE: DModule.PANE_MGR,
                    DField.TO_METHOD: DMethod.SET_PANE,
                    DField.NAME: DPane.MONEROD_TYPE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New P2Pool (remote) deployment
            elif leaf_data == DLabel.NEW and parent_data == DLabel.P2POOL_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.P2POOL,
                    DField.TO_MODULE: DModule.PANE_MGR,
                    DField.TO_METHOD: DMethod.SET_PANE,
                    DField.NAME: DPane.P2POOL_TYPE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New XMRig deployment
            elif leaf_data == DLabel.NEW and parent_data == DLabel.XMRIG_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.XMRIG,
                    DField.TO_MODULE: DModule.OPS_MGR,
                    DField.TO_METHOD: DMethod.GET_NEW,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            elif parent_data == DLabel.XMRIG_REMOTE_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.XMRIG_REMOTE,
                    DField.TO_MODULE: DModule.OPS_MGR,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                    DField.INSTANCE: leaf_data
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            elif event.node.parent.parent:
                grandparent_data = event.node.parent.parent.data
                #print(f"NavPane:on_tree_node_selected(): {grandparent_data}/{parent_data}/{leaf_data}")
                
                # View/Update a Monero deployment
                if grandparent_data == DLabel.MONEROD_SHORT:

                    monerod = self.ops_mgr.get_deployment(
                        elem_type=DElem.MONEROD, instance=parent_data)
                    #print(f"NavPane:on_tree_node_selected(): monerod: {monerod}")
                    
                    if leaf_data == DLabel.LOG_FILE:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.MONEROD,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.LOG_VIEWER,
                            DField.INSTANCE: parent_data
                        }

                    elif monerod.remote():
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.GET_DEPL,
                            DField.INSTANCE: leaf_data
                        }
                    else:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.MONEROD,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.GET_DEPL,
                            DField.INSTANCE: leaf_data
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a P2Pool deployment
                elif grandparent_data == DLabel.P2POOL_SHORT:

                    p2pool = self.ops_mgr.get_deployment(
                        elem_type=DElem.P2POOL, instance=parent_data)
                    # P2Pool log file
                    if leaf_data == DLabel.LOG_FILE:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.P2POOL,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.LOG_VIEWER,
                            DField.INSTANCE: parent_data
                        }
                    # Remote P2Pool
                    elif p2pool.remote():
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.GET_DEPL,
                            DField.INSTANCE: leaf_data
                        }
                    # Local P2Pool
                    else:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.P2POOL,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.GET_DEPL,
                            DField.INSTANCE: leaf_data
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a XMRig deployment
                elif grandparent_data == DLabel.XMRIG_SHORT:
                    #print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT}/{leaf_item.label}")
                    if leaf_data == DLabel.LOG_FILE:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.XMRIG,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.LOG_VIEWER,
                            DField.INSTANCE: parent_data
                        }
                        
                    else:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.XMRIG,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.GET_DEPL,
                            DField.INSTANCE: leaf_data
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # Chain Stats
                elif grandparent_data == DLabel.CHAIN_STATS:
                    if leaf_data == DLabel.LOG_FILE:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.INT_P2POOL,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.LOG_VIEWER,
                            DField.INSTANCE: parent_data
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

            elif leaf_data in (BLOCK, MINERS, HASH) and parent_data in (MAIN, MINI, NANO):
                chain = parent_data
                metric = leaf_data
                #print(f"NavPane:on_tree_node_selected(): {chain}/{metric}")
                form_data = {
                    DField.ELEMENT_TYPE: CHAIN,
                    DField.TO_MODULE: DModule.OPS_MGR,
                    DField.TO_METHOD: DMethod.PLOT,
                    CHAIN: chain,
                    DField.PLOT_TYPE: metric
                }
                self.post_message(Db4eMsg(self, form_data=form_data))


    def refresh_nav_pane(self) -> None:
        self.set_initialized()
        
        if not self.is_initialized():
            if not self.initial_branches_added:
                self.initial_branches_added = True
                # Initial setup
                self.depls.root.add_leaf(
                    f"{ICON[SETUP]} {DLabel.INITIAL_SETUP}", data=DLabel.INITIAL_SETUP)
                # Donations
                self.depls.root.add_leaf(
                    f"{ICON[GIFT]} {DLabel.DONATIONS}", data=DLabel.DONATIONS)
                return
            else:
                return

        if self.is_initialized() and self.initial_branches_added:
            self.depls.root.remove_children()
            self.initial_branches_added = False


        if not self.depls_branches_added:
            self.depls.root.add_leaf(
                f"{ICON[CORE]} {DLabel.DB4E}", data=DLabel.DB4E)
            self.monerod_tree = self.depls.root.add(
                f"{ICON[MON]} {DLabel.MONEROD_SHORT}", data=DLabel.MONEROD_SHORT, expand=True)
            self.p2pool_tree = self.depls.root.add(
                f"{ICON[P2P]} {DLabel.P2POOL_SHORT}", data=DLabel.P2POOL_SHORT, expand=True)
            self.xmrig_tree = self.depls.root.add(
                f"{ICON[XMR]} {DLabel.XMRIG_SHORT}", data=DLabel.XMRIG_SHORT, expand=True)
            self.xmrig_remote_tree = self.depls.root.add(
                f"{ICON[XMR]} {DLabel.XMRIG_REMOTE_SHORT}", data=DLabel.XMRIG_REMOTE_SHORT, expand=True)
            chain = self.depls.root.add(
                f"{ICON[CHAIN]} {DLabel.CHAIN_STATS}", data=DLabel.CHAIN_STATS, expand=True)
            main = chain.add(
                f"{ICON[MAIN]} {DLabel.MAIN_CHAIN}", data=DLabel.MAIN_CHAIN, expand=True)
            main.add_leaf(
                    f"{ICON[LOG]} {DLabel.LOG_FILE}", data=DLabel.LOG_FILE)            
            mini = chain.add(
                f"{ICON[MINI]} {DLabel.MINI_CHAIN}", data=DLabel.MINI_CHAIN, expand=True)            
            mini.add_leaf(
                    f"{ICON[LOG]} {DLabel.LOG_FILE}", data=DLabel.LOG_FILE)
            nano = chain.add(
                f"{ICON[NANO]} {DLabel.NANO_CHAIN}", data=DLabel.NANO_CHAIN, expand=True)
            nano.add_leaf(
                    f"{ICON[LOG]} {DLabel.LOG_FILE}", data=DLabel.LOG_FILE)


        self.monerod_tree.remove_children()
        self.monerod_tree.add_leaf(f"{ICON[NEW]} {DLabel.NEW}", data=DLabel.NEW)
        for monerod in self.ops_mgr.get_monerods():
            state = monerod.status()
            instance_branch = self.monerod_tree.add(
                f"{ICON[MON]} {monerod.instance()}", data=monerod.instance(), expand=True)
            instance_branch.add_leaf(
                f"{STATE_ICON[state]} {monerod.instance()}", data=monerod.instance())
            if not monerod.remote():
                instance_branch.add_leaf(
                    f"{ICON[LOG]} {DLabel.LOG_FILE}", data=DLabel.LOG_FILE)

        self.p2pool_tree.remove_children()
        self.p2pool_tree.add_leaf(f"{ICON[NEW]} {DLabel.NEW}", data=DLabel.NEW)
        for p2pool in self.ops_mgr.get_p2pools():
            state = p2pool.status()
            instance_branch = self.p2pool_tree.add(
                f"{ICON[P2P]} {p2pool.instance()}", data=p2pool.instance(), expand=True)
            instance_branch.add_leaf(
                f"{STATE_ICON[state]} {p2pool.instance()}", data=p2pool.instance())
            if not p2pool.remote():
                instance_branch.add_leaf(
                    f"{ICON[LOG]} {DLabel.LOG_FILE}", data=DLabel.LOG_FILE)

        self.xmrig_tree.remove_children()
        self.xmrig_tree.add_leaf(f"{ICON[NEW]} {DLabel.NEW}", data=DLabel.NEW)
        for xmrig in self.ops_mgr.get_xmrigs():
            state = xmrig.status()
            instance_branch = self.xmrig_tree.add(
                f"{ICON[XMR]} {xmrig.instance()}", data=xmrig.instance(), expand=True)
            instance_branch.add_leaf(
                f"{STATE_ICON[state]} {xmrig.instance()}", data=xmrig.instance())
            instance_branch.add_leaf(
                f"{ICON[LOG]} {DLabel.LOG_FILE}", data=DLabel.LOG_FILE)
        
        self.xmrig_remote_tree.remove_children()
        for remote_xmrig in self.ops_mgr.get_xmrigs_remote():
            state = remote_xmrig.status()
            self.xmrig_remote_tree.add_leaf(
                f"{STATE_ICON[state]} {remote_xmrig.instance()}", data=remote_xmrig.instance())
        
        if not self.depls_branches_added:
            self.depls_branches_added = True

            # Add Log link
            self.depls.root.add_leaf(f"{ICON[LOG]} {DLabel.TUI_LOG}", data=DLabel.TUI_LOG)

            # Add Donations link
            self.depls.root.add_leaf(f"{ICON[GIFT]} {DLabel.DONATIONS}", data=DLabel.DONATIONS)

        


    def set_initialized(self):
        if not self._initialized:  
            self._initialized = self.ops_mgr.depl_client.is_initialized()
        return self._initialized

