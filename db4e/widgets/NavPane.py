"""
Widgets/NavPane.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual import work
from textual.widgets import Tree
from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer

from db4e.client.HealthClient import HealthClient
from db4e.db.DeplDb import DeplDb

from db4e.messages.Db4EMsg import Db4EMsg

from db4e.constants.DElem import DElem
from db4e.constants.DField import DField
from db4e.constants.DLabel import DLabel
from db4e.constants.DMethod import DMethod
from db4e.constants.DModule import DModule
from db4e.constants.DPane import DPane
from db4e.constants.DStatus import DStatus

# Icon dictionary keys
CORE = "CORE"
CHAIN = "CHAIN"
DEPL = "DEPL"
GIFT = "GIFT"
LOG = "LOG"
MINERS = "MINERS"
MON = "MON"
NEW = "NEW"
P2P = "P2P"
SETUP = "SETUP"
XMR = "XMR"

ICON = {
    CHAIN: "🧵",
    CORE: "📡",
    DEPL: "💻",
    GIFT: "🎉",
    LOG: "📚",
    MINERS: "👷",
    MON: "🌿",
    NEW: "🔧",
    P2P: "🌊",
    SETUP: "⚙️",
    XMR: "🔍",
}
#    XMR: "⛏️",

STATE_ICON = {
    DStatus.GOOD: "🟢",
    DStatus.WARN: "🟡",
    DStatus.ERROR: "🔴",
    DStatus.UNKNOWN: "⚪",
}


class NavPane(Container):

    def __init__(self, depl_db: DeplDb, health_client: HealthClient):
        super().__init__()
        self.depl_db = depl_db
        self.health_client = health_client
        self._initialized = False

        # Deployments tree
        self.depls = Tree(f"{ICON[DEPL]} {DLabel.DEPLOYMENTS}")
        self.depls.guide_depth = 3
        self.depls.root.expand()

        self.depls_branches_added, self.initial_branches_added = False, False

        self.depls_branch_state = {DElem.MONEROD: {}, DElem.P2POOL: {}, DElem.XMRIG: {}}

        self.refresh_nav_pane()

    def check_initialized(self):
        if self.is_initialized():
            return
        else:
            self.depl_db.check_initialized()
            if self.depl_db.is_initialized():
                self._initialized = True
            else:
                self._initialized = False

    def compose(self) -> ComposeResult:
        yield Vertical(
            ScrollableContainer(
                Vertical(
                    self.depls,
                )
            ),
            id="nav_pane",
        )

    def is_initialized(self) -> bool:
        # print(f"NavPane:is_initialized(): {self._initialized}")
        return self._initialized

    async def on_mount(self) -> None:
        self.set_interval(2, self.refresh_nav_pane)

    @work(exclusive=True)
    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        form_data = {}
        if not event.node.children and event.node.parent:
            leaf_data = event.node.data
            parent_data = event.node.parent.data
            # print(
            #    f"NavPane:on_tree_node_selected(): leaf_data ({leaf_data}), parent_data ({parent_data})"
            # )

            # Initial Setup
            if leaf_data == DLabel.INITIAL_SETUP:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.DB4E,
                    DField.TO_MODULE: DModule.INSTALL_MGR,
                    DField.TO_METHOD: DMethod.INITIAL_SETUP_PROCEED,
                }

            # TUI Log
            elif leaf_data == DLabel.TUI_LOG:
                form_data = {
                    DField.ELEMENT_TYPE: DField.TUI_LOG,
                    DField.TO_MODULE: DModule.OPS_DB,
                    DField.TO_METHOD: DMethod.GET_TUI_LOG,
                }

            # Donations
            elif leaf_data == DLabel.DONATIONS:
                form_data = {
                    DField.ELEMENT_TYPE: DField.DONATIONS,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.SET_PANE,
                }

            # Main, Mini and Nano Chain Stats
            elif parent_data == DLabel.CHAIN_STATS:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.P2POOL_INTERNAL,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                    DField.INSTANCE: leaf_data,
                }

            ## Deployed Elements

            ## Core
            # View/Update Db4E Core
            elif leaf_data == DLabel.DB4E:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.DB4E,
                    DField.INSTANCE: DElem.DB4E,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                }

            ## New Deployments
            # Monero
            elif leaf_data == DLabel.NEW and parent_data == DLabel.MONEROD_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.MONEROD,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_NEW,
                }
            # Remote Monero
            elif leaf_data == DLabel.NEW and parent_data == DLabel.MONEROD_REMOTE_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_NEW,
                }
            # P2Pool
            elif leaf_data == DLabel.NEW and parent_data == DLabel.P2POOL_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.P2POOL,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_NEW,
                }
            # P2Pool Remote
            elif leaf_data == DLabel.NEW and parent_data == DLabel.P2POOL_REMOTE_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_NEW,
                }
            # XMRig
            elif leaf_data == DLabel.NEW and parent_data == DLabel.XMRIG_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.XMRIG,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_NEW,
                }

            ## View/Edit
            # Monero
            elif parent_data == DLabel.MONEROD_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.MONEROD,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                    DField.INSTANCE: leaf_data,
                }
            # Remote Monero
            elif parent_data == DLabel.MONEROD_REMOTE_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                    DField.INSTANCE: leaf_data,
                }
            # P2Pool
            elif parent_data == DLabel.P2POOL_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.P2POOL,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                    DField.INSTANCE: leaf_data,
                }
            # Remote P2Pool
            elif parent_data == DLabel.P2POOL_REMOTE_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                    DField.INSTANCE: leaf_data,
                }
            # XMRig
            elif parent_data == DLabel.XMRIG_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.XMRIG,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                    DField.INSTANCE: leaf_data,
                }
            # Remote XMRig
            elif parent_data == DLabel.XMRIG_REMOTE_SHORT:
                form_data = {
                    DField.ELEMENT_TYPE: DElem.XMRIG_REMOTE,
                    DField.TO_MODULE: DModule.NAV_HANDLER,
                    DField.TO_METHOD: DMethod.GET_DEPL,
                    DField.INSTANCE: leaf_data,
                }

            elif event.node.parent.parent:
                grandparent_data = event.node.parent.parent.data

                print(
                    f"NavPane:on_tree_node_selected(): %s/%s/%s"
                    % (grandparent_data, parent_data, leaf_data)
                )

                ## Local deployment logfiles
                # Monero
                if grandparent_data == DLabel.MONEROD_SHORT:
                    monerod = self.depl_db.get_deployment(
                        elem_type=DElem.MONEROD, instance=parent_data
                    )
                    if leaf_data == DLabel.LOG_FILE:  # Log file nav item
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.MONEROD,
                            DField.TO_MODULE: DModule.NAV_HANDLER,
                            DField.TO_METHOD: DMethod.LOG_VIEWER,
                            DField.INSTANCE: monerod,
                        }
                    # View edit deployment
                    else:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.MONEROD,
                            DField.TO_MODULE: DModule.NAV_HANDLER,
                            DField.TO_METHOD: DMethod.GET_DEPL,
                            DField.INSTANCE: monerod,
                        }

                # Existing remote Monero deployment
                elif grandparent_data == DLabel.MONEROD_REMOTE_SHORT:
                    monerod = self.depl_db.get_deployment(
                        elem_type=DElem.MONEROD_REMOTE, instance=parent_data
                    )
                    # View/edit deployment
                    form_data = {
                        DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                        DField.TO_MODULE: DModule.NAV_HANDLER,
                        DField.TO_METHOD: DMethod.GET_DEPL,
                        DField.INSTANCE: monerod,
                    }

                # Exiting P2Pool deployment
                elif grandparent_data == DLabel.P2POOL_SHORT:
                    p2pool = self.depl_db.get_deployment(
                        elem_type=DElem.P2POOL, instance=parent_data
                    )
                    # View log file
                    if leaf_data == DLabel.LOG_FILE:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.P2POOL,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.LOG_VIEWER,
                            DField.INSTANCE: p2pool,
                        }
                    # View/edit deployment
                    else:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.P2POOL,
                            DField.TO_MODULE: DModule.NAV_HANDLER,
                            DField.TO_METHOD: DMethod.GET_DEPL,
                            DField.INSTANCE: p2pool,
                        }

                # Exiting remote P2Pool deployment
                elif grandparent_data == DLabel.P2POOL_REMOTE_SHORT:

                    p2pool = self.depl_db.get_deployment(
                        elem_type=DElem.P2POOL_REMOTE, instance=parent_data
                    )
                    form_data = {
                        DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                        DField.TO_MODULE: DModule.NAV_HANDLER,
                        DField.TO_METHOD: DMethod.GET_DEPL,
                        DField.INSTANCE: p2pool,
                    }

                # Existing XMRig deployment
                elif grandparent_data == DLabel.XMRIG_SHORT:
                    # print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT}/{leaf_item.label}")
                    if leaf_data == DLabel.LOG_FILE:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.XMRIG,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.LOG_VIEWER,
                            DField.INSTANCE: parent_data,
                        }

                    else:
                        form_data = {
                            DField.ELEMENT_TYPE: DElem.XMRIG,
                            DField.TO_MODULE: DModule.OPS_MGR,
                            DField.TO_METHOD: DMethod.GET_DEPL,
                            DField.INSTANCE: leaf_data,
                        }

                # Existing remote XMRig deployment
                elif grandparent_data == DLabel.XMRIG_SHORT:
                    # print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT}/{leaf_item.label}")
                    form_data = {
                        DField.ELEMENT_TYPE: DElem.XMRIG,
                        DField.TO_MODULE: DModule.OPS_MGR,
                        DField.TO_METHOD: DMethod.GET_DEPL,
                        DField.INSTANCE: leaf_data,
                    }
            # print(f"Posting message with form_data: {form_data}")
            self.post_message(Db4EMsg(self, form_data=form_data))

    def refresh_nav_pane(self) -> None:
        self.check_initialized()
        if not self.is_initialized():
            if not self.initial_branches_added:
                self.initial_branches_added = True
                # Initial setup
                self.depls.root.add_leaf(
                    f"{ICON[SETUP]} {DLabel.INITIAL_SETUP}", data=DLabel.INITIAL_SETUP
                )
                # Donations
                self.depls.root.add_leaf(
                    f"{ICON[GIFT]} {DLabel.DONATIONS}", data=DLabel.DONATIONS
                )
                return
            else:
                return

        if self.is_initialized() and self.initial_branches_added:
            self.depls.root.remove_children()
            self.initial_branches_added = False

        if not self.depls_branches_added:
            self.depls.root.add_leaf(f"{ICON[CORE]} {DLabel.DB4E}", data=DLabel.DB4E)
            self.monerod_tree = self.depls.root.add(
                f"{ICON[MON]} {DLabel.MONEROD_SHORT}",
                data=DLabel.MONEROD_SHORT,
                expand=True,
            )
            self.monerod_remote_tree = self.depls.root.add(
                f"{ICON[MON]} {DLabel.MONEROD_REMOTE_SHORT}",
                data=DLabel.MONEROD_REMOTE_SHORT,
                expand=True,
            )
            self.p2pool_tree = self.depls.root.add(
                f"{ICON[P2P]} {DLabel.P2POOL_SHORT}",
                data=DLabel.P2POOL_SHORT,
                expand=True,
            )
            self.p2pool_remote_tree = self.depls.root.add(
                f"{ICON[P2P]} {DLabel.P2POOL_REMOTE_SHORT}",
                data=DLabel.P2POOL_REMOTE_SHORT,
                expand=True,
            )
            self.xmrig_tree = self.depls.root.add(
                f"{ICON[XMR]} {DLabel.XMRIG_SHORT}",
                data=DLabel.XMRIG_SHORT,
                expand=True,
            )
            self.xmrig_remote_tree = self.depls.root.add(
                f"{ICON[XMR]} {DLabel.XMRIG_REMOTE_SHORT}",
                data=DLabel.XMRIG_REMOTE_SHORT,
                expand=True,
            )
            self.chain = self.depls.root.add(
                f"{ICON[CHAIN]} {DLabel.CHAIN_STATS}",
                data=DLabel.CHAIN_STATS,
                expand=True,
            )

        self.monerod_tree.remove_children()
        self.monerod_tree.add_leaf(f"{ICON[NEW]} {DLabel.NEW}", data=DLabel.NEW)
        for monerod in self.depl_db.get_monerods():
            state = monerod.status()
            self.monerod_tree.add_leaf(
                f"{STATE_ICON[state]} {monerod.instance()}", data=monerod.instance()
            )

        self.monerod_remote_tree.remove_children()
        self.monerod_remote_tree.add_leaf(f"{ICON[NEW]} {DLabel.NEW}", data=DLabel.NEW)
        for monerod in self.depl_db.get_monerod_remotes():
            state = self.health_client.get_status(monerod)
            self.monerod_remote_tree.add_leaf(
                f"{STATE_ICON[state]} {monerod.instance()}", data=monerod.instance()
            )

        self.p2pool_tree.remove_children()
        self.p2pool_tree.add_leaf(f"{ICON[NEW]} {DLabel.NEW}", data=DLabel.NEW)
        for p2pool in self.depl_db.get_p2pools():
            state = p2pool.status()
            self.p2pool_tree.add_leaf(
                f"{STATE_ICON[state]} {p2pool.instance()}", data=p2pool.instance()
            )

        self.p2pool_remote_tree.remove_children()
        self.p2pool_remote_tree.add_leaf(f"{ICON[NEW]} {DLabel.NEW}", data=DLabel.NEW)
        for p2pool in self.depl_db.get_p2pool_remotes():
            state = self.health_client.get_status(p2pool)
            self.p2pool_remote_tree.add_leaf(
                f"{STATE_ICON[state]} {p2pool.instance()}", data=p2pool.instance()
            )

        self.chain.remove_children()
        for int_p2pool in self.depl_db.get_p2pool_internals():
            state = int_p2pool.status()
            instance = int_p2pool.instance()
            self.chain.add_leaf(f"{STATE_ICON[state]} {instance}", data=instance)

        self.xmrig_tree.remove_children()
        self.xmrig_tree.add_leaf(f"{ICON[NEW]} {DLabel.NEW}", data=DLabel.NEW)
        for xmrig in self.depl_db.get_xmrigs():
            state = xmrig.status()
            self.xmrig_tree.add_leaf(
                f"{STATE_ICON[state]} {xmrig.instance()}", data=xmrig.instance()
            )

        self.xmrig_remote_tree.remove_children()
        for remote_xmrig in self.depl_db.get_xmrig_remotes():
            remote_xmrig.timestamp(
                self.depl_db.get_remote_xmrig_timestamp(remote_xmrig)
            )
            state = remote_xmrig.status()
            self.xmrig_remote_tree.add_leaf(
                f"{STATE_ICON[state]} {remote_xmrig.instance()}",
                data=remote_xmrig.instance(),
            )

        if not self.depls_branches_added:
            self.depls_branches_added = True

            # Add Console Log item
            self.depls.root.add_leaf(
                f"{ICON[LOG]} {DLabel.TUI_LOG}", data=DLabel.TUI_LOG
            )

            # Add Donations item
            self.depls.root.add_leaf(
                f"{ICON[GIFT]} {DLabel.DONATIONS}", data=DLabel.DONATIONS
            )
