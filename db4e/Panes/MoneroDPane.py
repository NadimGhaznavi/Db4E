
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
    intro_label = Label("", classes=DForm.INTRO, id=DForm.INTRO)
    any_ip_label = Label("", classes=DForm.STATIC)
    blockchain_dir_label = Label("", classes=DForm.STATIC)
    config_label = Label("", classes=DForm.STATIC)
    instance_label = Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC)

    in_peers_input = Input(
        id=DForm.IN_PEERS_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    instance_input = Input(
        compact=True, id=DForm.INSTANCE_INPUT, restrict=f"[a-zA-Z0-9_\-]*",
        classes=DForm.INPUT_30)
    log_level_input = Input(
        id=DForm.LOG_LEVEL_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    max_log_files_input = Input(
        id=DForm.MAX_LOG_FILES_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    max_log_size_input = Input(
        id=DForm.MAX_LOG_SIZE_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    out_peers_input = Input(
        id=DForm.OUT_PEERS_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    p2p_bind_port_input = Input(
        id=DForm.P2P_BIND_PORT_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    priority_node_1_input = Input(
        id=DForm.PRIORITY_NODE_1_INPUT, restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=DForm.INPUT_30)
    priority_port_1_input = Input(
        id=DForm.PRIORITY_PORT_1_INPUT, restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=DForm.INPUT_30)
    priority_node_2_input = Input(
        id=DForm.PRIORITY_NODE_2_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    priority_port_2_input = Input(
        id=DForm.PRIORITY_PORT_2_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    rpc_bind_port_input = Input(
        compact=True, id=DForm.RPC_BIND_PORT_INPUT, restrict=f"[0-9]*",
        classes=DForm.INPUT_30)
    zmq_pub_port_input = Input(
        compact=True, id=DForm.ZMQ_PUB_PORT_INPUT, restrict=f"[0-9]*",
        classes=DForm.INPUT_30)
    zmq_rpc_port_input = Input(
        compact=True, id=DForm.ZMQ_RPC_PORT_INPUT, restrict=f"[0-9]*",
        classes=DForm.INPUT_30)

    health_msgs = Label()

    delete_button = Button(label=DLabel.DELETE, id=DButton.DELETE)
    disable_button = Button(label=DLabel.STOP, id=DButton.DISABLE)
    enable_button = Button(label=DLabel.START, id=DButton.ENABLE)
    new_button = Button(label=DLabel.NEW, id=DButton.NEW)
    update_button = Button(label=DLabel.UPDATE, id=DButton.UPDATE)
    view_log_button = Button(label=DLabel.VIEW_LOG, id=DButton.VIEW_LOG)
    

    def compose(self):
        # Local Monero daemon deployment form
        yield Vertical(
            ScrollableContainer(
                self.intro_label,

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.IN_PEERS, classes=DForm.FORM_LABEL),
                        self.in_peers_input),
                    Horizontal(
                        Label(DLabel.OUT_PEERS, classes=DForm.FORM_LABEL),
                        self.out_peers_input),
                    Horizontal(
                        Label(DLabel.P2P_BIND_PORT, classes=DForm.FORM_LABEL),
                        self.p2p_bind_port_input),
                    Horizontal(
                        Label(DLabel.RPC_BIND_PORT, classes=DForm.FORM_LABEL),
                        self.rpc_bind_port_input),
                    Horizontal(
                        Label(DLabel.ZMQ_PUB_PORT, classes=DForm.FORM_LABEL),
                        self.zmq_pub_port_input),
                    Horizontal(
                        Label(DLabel.ZMQ_RPC_PORT, classes=DForm.FORM_LABEL),
                        self.zmq_rpc_port_input),
                    Horizontal(
                        Label(DLabel.LOG_LEVEL, classes=DForm.FORM_LABEL),
                        self.log_level_input),
                    Horizontal(
                        Label(DLabel.MAX_LOG_FILES, classes=DForm.FORM_LABEL),
                        self.max_log_files_input),
                    Horizontal(
                        Label(DLabel.MAX_LOG_SIZE, classes=DForm.FORM_LABEL),
                        self.max_log_size_input),
                    Horizontal(
                        Label(DLabel.PRIORITY_NODE_1, classes=DForm.FORM_LABEL),
                        self.priority_node_1_input),
                    Horizontal(
                        Label(DLabel.PRIORITY_PORT_1, classes=DForm.FORM_LABEL),
                        self.priority_port_1_input),
                    Horizontal(
                        Label(DLabel.PRIORITY_NODE_2, classes=DForm.FORM_LABEL),
                        self.priority_node_2_input),
                    Horizontal(
                        Label(DLabel.PRIORITY_PORT_2, classes=DForm.FORM_LABEL),
                        self.priority_port_2_input),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL),
                        self.config_label),
                    Horizontal(
                        Label(DLabel.BLOCKCHAIN_DIR, classes=DForm.FORM_LABEL),
                        self.blockchain_dir_label),
                    classes=DForm.FORM_16, id=DForm.FORM_BOX),
                    
                    Vertical(
                        self.health_msgs,
                        classes=DForm.HEALTH_BOX, id=DForm.HEALTH_BOX
                    ),

                Vertical(
                    Horizontal(
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.view_log_button,
                        self.disable_button,
                        self.delete_button,
                        classes=DForm.BUTTON_ROW))),
                
            classes=DForm.PANE_BOX)
    

    def on_mount(self):
        form_box = self.query_one("#" + DForm.FORM_BOX, Vertical)
        form_box.border_subtitle = DLabel.CONFIG
        health_box = self.query_one("#" + DForm.HEALTH_BOX, Vertical)
        health_box.border_subtitle = DLabel.STATUS


    def set_data(self, monerod: MoneroD):
        self.monerod = monerod
        self.instance_input.value = monerod.instance()
        self.instance_label.update(monerod.instance())
        self.config_label.update(monerod.config_file())
        self.blockchain_dir_label.update(monerod.blockchain_dir())
        self.in_peers_input.value = str(monerod.in_peers())
        self.out_peers_input.value = str(monerod.out_peers())
        self.p2p_bind_port_input.value = str(monerod.p2p_bind_port())
        self.rpc_bind_port_input.value = str(monerod.rpc_bind_port())
        self.zmq_pub_port_input.value = str(monerod.zmq_pub_port())
        self.zmq_rpc_port_input.value = str(monerod.zmq_rpc_port())
        self.log_level_input.value = str(monerod.log_level())
        self.max_log_files_input.value = str(monerod.max_log_files())
        self.max_log_size_input.value = str(monerod.max_log_size())
        self.priority_node_1_input.value = str(monerod.priority_node_1())
        self.priority_port_1_input.value = str(monerod.priority_port_1())
        self.priority_node_2_input.value = str(monerod.priority_node_2())
        self.priority_port_2_input.value = str(monerod.priority_port_2())

        # Configure button visibility
        if monerod.instance():
            INTRO = "Configure the settings for the " \
            f"[bold cyan]{monerod.instance()} {DLabel.MONEROD}[/] deployment."

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
            INTRO = "Configure the settings for a new " \
            f"[bold cyan]{DLabel.MONEROD}[/] deployment."
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.intro_label.update(INTRO)
        self.health_msgs.update(gen_results_table(monerod.pop_msgs()))


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        self.monerod.instance(self.query_one("#" + DForm.INSTANCE_INPUT, Input).value)
        self.monerod.in_peers(self.query_one("#" + DForm.IN_PEERS_INPUT, Input).value)
        self.monerod.out_peers(self.query_one("#" + DForm.OUT_PEERS_INPUT, Input).value)
        self.monerod.log_level(self.query_one("#" + DForm.LOG_LEVEL_INPUT, Input).value)
        self.monerod.max_log_files(self.query_one("#" + DForm.MAX_LOG_FILES_INPUT, Input).value)
        self.monerod.max_log_size(self.query_one("#" + DForm.MAX_LOG_SIZE_INPUT, Input).value)
        self.monerod.p2p_bind_port(self.query_one("#" + DForm.P2P_BIND_PORT_INPUT, Input).value)
        self.monerod.priority_node_1(self.query_one("#" + DForm.PRIORITY_NODE_1_INPUT, Input).value)
        self.monerod.priority_port_1(self.query_one("#" + DForm.PRIORITY_PORT_1_INPUT, Input).value)
        self.monerod.priority_node_2(self.query_one("#" + DForm.PRIORITY_NODE_2_INPUT, Input).value)
        self.monerod.priority_port_2(self.query_one("#" + DForm.PRIORITY_PORT_2_INPUT, Input).value)
        self.monerod.rpc_bind_port(self.query_one("#" + DForm.RPC_BIND_PORT_INPUT, Input).value)
        self.monerod.zmq_pub_port(self.query_one("#" + DForm.ZMQ_PUB_PORT_INPUT, Input).value)
        self.monerod.zmq_rpc_port(self.query_one("#" + DForm.ZMQ_RPC_PORT_INPUT, Input).value)

        if button_id == DButton.NEW:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod
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
                DField.INSTANCE: self.monerod.instance()
            }               

        self.app.post_message(Db4eMsg(self, form_data=form_data))                              
        # self.app.post_message(Db4eMsg(self, form_data=form_data))