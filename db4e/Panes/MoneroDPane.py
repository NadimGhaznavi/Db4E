"""
db4e/Panes/MoneroDPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Label, Input, Button, Checkbox

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.Helper import gen_results_table
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DModule import DModule
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DJob import DJob
from db4e.Constants.DButton import DButton
from db4e.Constants.DForm import DForm


color = "#9cae41"
hi = "#d7e556"


class MoneroDPane(Container):

    def compose(self):
        # Local Monero daemon deployment form
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        Input(
                            compact=True,
                            id=DForm.INSTANCE_INPUT,
                            restrict=f"[a-zA-Z0-9_\-]*",
                            classes=DForm.INPUT_30,
                        ),
                        Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.IN_PEERS, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.IN_PEERS_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.OUT_PEERS, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.OUT_PEERS_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.P2P_BIND_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.P2P_BIND_PORT_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.RPC_BIND_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            compact=True,
                            id=DForm.RPC_BIND_PORT_INPUT,
                            restrict=f"[0-9]*",
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.ZMQ_PUB_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            compact=True,
                            id=DForm.ZMQ_PUB_PORT_INPUT,
                            restrict=f"[0-9]*",
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.ZMQ_RPC_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            compact=True,
                            id=DForm.ZMQ_RPC_PORT_INPUT,
                            restrict=f"[0-9]*",
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.LOG_LEVEL, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.LOG_LEVEL_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.MAX_LOG_FILES, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.MAX_LOG_FILES_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.MAX_LOG_SIZE, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.MAX_LOG_SIZE_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.PRIORITY_NODE_1, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.PRIORITY_NODE_1_INPUT,
                            restrict=f"[a-zA-Z0-9_\-]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.PRIORITY_PORT_1, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.PRIORITY_PORT_1_INPUT,
                            restrict=f"[a-zA-Z0-9_\-]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.PRIORITY_NODE_2, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.PRIORITY_NODE_2_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.PRIORITY_PORT_2, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.PRIORITY_PORT_2_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.CONFIG_FILE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.BLOCKCHAIN_DIR, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.BLOCKCHAIN_DIR_LABEL, classes=DForm.STATIC),
                    ),
                    classes=DForm.FORM_16,
                    id=DForm.FORM_BOX,
                ),
                Vertical(
                    Label("", id=DForm.HEALTH_LABEL, classes=DForm.HEALTH_LABEL),
                    classes=DForm.HEALTH_BOX,
                    id=DForm.HEALTH_BOX,
                ),
                Vertical(
                    Horizontal(
                        Button(label=DLabel.NEW, id=DButton.NEW),
                        Button(label=DLabel.UPDATE, id=DButton.UPDATE),
                        Button(label=DLabel.START, id=DButton.ENABLE),
                        Button(label=DLabel.VIEW_LOG, id=DButton.VIEW_LOG),
                        Button(label=DLabel.STOP, id=DButton.DISABLE),
                        Button(label=DLabel.DELETE, id=DButton.DELETE),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_mount(self):
        form_box = self.query_one("#" + DForm.FORM_BOX, Vertical)
        form_box.border_subtitle = DLabel.CONFIG
        health_box = self.query_one("#" + DForm.HEALTH_BOX, Vertical)
        health_box.border_subtitle = DLabel.STATUS

    def set_data(self, monerod: MoneroD):
        self.monerod = monerod
        self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value = monerod.instance()
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(monerod.instance())
        self.query_one(f"#{DForm.CONFIG_FILE_LABEL}", Label).update(
            monerod.config_file()
        )
        self.query_one(f"#{DForm.BLOCKCHAIN_DIR_LABEL}", Label).update(
            monerod.blockchain_dir()
        )
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(monerod.pop_msgs())
        )
        self.query_one(f"#{DForm.IN_PEERS_INPUT}", Input).value = str(
            monerod.in_peers()
        )
        self.query_one(f"#{DForm.OUT_PEERS_INPUT}", Input).value = str(
            monerod.out_peers()
        )
        self.query_one(f"#{DForm.P2P_BIND_PORT_INPUT}", Input).value = str(
            monerod.p2p_bind_port()
        )
        self.query_one(f"#{DForm.RPC_BIND_PORT_INPUT}", Input).value = str(
            monerod.rpc_bind_port()
        )
        self.query_one(f"#{DForm.ZMQ_PUB_PORT_INPUT}", Input).value = str(
            monerod.zmq_pub_port()
        )
        self.query_one(f"#{DForm.ZMQ_RPC_PORT_INPUT}", Input).value = str(
            monerod.zmq_rpc_port()
        )
        self.query_one(f"#{DForm.LOG_LEVEL_INPUT}", Input).value = str(
            monerod.log_level()
        )
        self.query_one(f"#{DForm.MAX_LOG_FILES_INPUT}", Input).value = str(
            monerod.max_log_files()
        )
        self.query_one(f"#{DForm.MAX_LOG_SIZE_INPUT}", Input).value = str(
            monerod.max_log_size()
        )
        self.query_one(f"#{DForm.PRIORITY_NODE_1_INPUT}", Input).value = str(
            monerod.priority_node_1()
        )
        self.query_one(f"#{DForm.PRIORITY_PORT_1_INPUT}", Input).value = str(
            monerod.priority_port_1()
        )
        self.query_one(f"#{DForm.PRIORITY_NODE_2_INPUT}", Input).value = str(
            monerod.priority_node_2()
        )
        self.query_one(f"#{DForm.PRIORITY_PORT_2_INPUT}", Input).value = str(
            monerod.priority_port_2()
        )

        # Configure button visibility
        if monerod.instance():
            INTRO = (
                "Configure the settings for the "
                f"[bold cyan]{monerod.instance()} {DLabel.MONEROD}[/] deployment."
            )

            # This is an update operation
            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)

            if monerod.enabled():
                self.remove_class(DField.DISABLE)
                self.add_class(DField.ENABLE)
            else:
                self.remove_class(DField.ENABLE)
                self.add_class(DField.DISABLE)

        else:
            # This is a new operation
            INTRO = (
                "Configure the settings for a new "
                f"[bold cyan]{DLabel.MONEROD}[/] deployment."
            )
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.query_one(f"#{DForm.INTRO}", Label).update(INTRO)
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(monerod.pop_msgs())
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        self.monerod.instance(self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value)
        self.monerod.in_peers(self.query_one(f"#{DForm.IN_PEERS_INPUT}", Input).value)
        self.monerod.out_peers(self.query_one(f"#{DForm.OUT_PEERS_INPUT}", Input).value)
        self.monerod.log_level(self.query_one(f"#{DForm.LOG_LEVEL_INPUT}", Input).value)
        self.monerod.max_log_files(
            self.query_one(f"#{DForm.MAX_LOG_FILES_INPUT}", Input).value
        )
        self.monerod.max_log_size(
            self.query_one(f"#{DForm.MAX_LOG_SIZE_INPUT}", Input).value
        )
        self.monerod.p2p_bind_port(
            self.query_one(f"#{DForm.P2P_BIND_PORT_INPUT}", Input).value
        )
        self.monerod.priority_node_1(
            self.query_one(f"#{DForm.PRIORITY_NODE_1_INPUT}", Input).value
        )
        self.monerod.priority_port_1(
            self.query_one(f"#{DForm.PRIORITY_PORT_1_INPUT}", Input).value
        )
        self.monerod.priority_node_2(
            self.query_one(f"#{DForm.PRIORITY_NODE_2_INPUT}", Input).value
        )
        self.monerod.priority_port_2(
            self.query_one(f"#{DForm.PRIORITY_PORT_2_INPUT}", Input).value
        )
        self.monerod.rpc_bind_port(
            self.query_one(f"#{DForm.RPC_BIND_PORT_INPUT}", Input).value
        )
        self.monerod.zmq_pub_port(
            self.query_one(f"#{DForm.ZMQ_PUB_PORT_INPUT}", Input).value
        )
        self.monerod.zmq_rpc_port(
            self.query_one(f"#{DForm.ZMQ_RPC_PORT_INPUT}", Input).value
        )

        if button_id == DButton.NEW:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.UPDATE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.ENABLE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.ENABLE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.DISABLE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DISABLE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DELETE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }
        elif button_id == DButton.VIEW_LOG:
            form_data = {
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.LOG_VIEWER,
                DField.INSTANCE: self.monerod.instance(),
            }

        self.app.post_message(Db4eMsg(self, form_data=form_data))
