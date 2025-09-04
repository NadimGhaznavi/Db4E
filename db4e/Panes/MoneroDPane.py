"""
db4e/Panes/MoneroDPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Label, Input, Button, MarkdownViewer

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Modules.MoneroD import MoneroD
from db4e.Modules.Helper import gen_results_table
from db4e.Constants.Fields import (
    PANE_BOX_FIELD, FORM_INPUT_30_FIELD, FORM_INTRO_FIELD, FORM_LABEL_FIELD, 
    STATIC_CONTENT_FIELD, HEALTH_BOX_FIELD, NEW_FIELD, ENABLE_FIELD, DISABLE_FIELD,
    ELEMENT_TYPE_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD, ELEMENT_FIELD,
    MONEROD_FIELD, ADD_DEPLOYMENT_FIELD, OPS_MGR_FIELD, INSTANCE_FIELD,
    FORM_16_FIELD, DEPLOYMENT_MGR_FIELD)
from db4e.Constants.Labels import (
    CONFIG_FILE_LABLE, MONEROD_LABEL, INSTANCE_LABEL, IN_PEERS_LABEL, OUT_PEERS_LABEL,
    LOG_LEVEL_LABEL, MAX_LOG_FILES_LABEL, MAX_LOG_SIZE_LABEL, P2P_BIND_PORT_LABEL,
    RPC_BIND_PORT_LABEL, ZMQ_PUB_PORT_LABEL, DATA_DIR_LABEL, 
    PRIORITY_NODE_1_LABEL, PRIORITY_PORT_1_LABEL, PRIORITY_NODE_2_LABEL, 
    PRIORITY_PORT_2_LABEL, ZMQ_RPC_PORT_LABEL)
from db4e.Constants.Buttons import (
    DELETE_BUTTON_FIELD, NEW_BUTTON_FIELD, BUTTON_ROW_FIELD, UPDATE_BUTTON_FIELD, 
    DELETE_LABEL, UPDATE_LABEL, NEW_LABEL, ENABLE_BUTTON_FIELD, ENABLE_LABEL,
    DISABLE_BUTTON_FIELD, DISABLE_LABEL)
from db4e.Constants.Jobs import (
    JOB_QUEUE_FIELD, POST_JOB_FIELD, OP_FIELD, DELETE_FIELD, UPDATE_FIELD)

color = "#9cae41"
hi = "#d7e556"

class MoneroDPane(Container):

    config_label = Label("", classes=STATIC_CONTENT_FIELD)
    any_ip_label = Label("", classes=STATIC_CONTENT_FIELD)
    data_dir_label = Label("", classes=STATIC_CONTENT_FIELD)
    instance_label = Label("", id="instance_label",classes=STATIC_CONTENT_FIELD)

    in_peers_input = Input(
        id="in_peers_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    instance_input = Input(
        compact=True, id="instance_input", restrict=f"[a-zA-Z0-9_\-]*",
        classes=FORM_INPUT_30_FIELD)
    log_level_input = Input(
        id="log_level_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    max_log_files_input = Input(
        id="max_log_files_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    max_log_size_input = Input(
        id="max_log_size_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    out_peers_input = Input(
        id="out_peers_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    p2p_bind_port_input = Input(
        id="p2p_bind_port_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    priority_node_1_input = Input(
        id="priority_node_1_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    priority_port_1_input = Input(
        id="priority_port_1_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    priority_node_2_input = Input(
        id="priority_node_2_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    priority_port_2_input = Input(
        id="priority_port_2_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    rpc_bind_port_input = Input(
        compact=True, id="rpc_bind_port_input", restrict=f"[0-9]*",
        classes=FORM_INPUT_30_FIELD)
    zmq_pub_port_input = Input(
        compact=True, id="zmq_pub_port_input", restrict=f"[0-9]*",
        classes=FORM_INPUT_30_FIELD)
    zmq_rpc_port_input = Input(
        compact=True, id="zmq_rpc_port_input", restrict=f"[0-9]*",
        classes=FORM_INPUT_30_FIELD)

    health_msgs = Label()

    delete_button = Button(label=DELETE_LABEL, id=DELETE_BUTTON_FIELD)
    disable_button = Button(label=DISABLE_LABEL, id=DISABLE_BUTTON_FIELD)
    enable_button = Button(label=ENABLE_LABEL, id=ENABLE_BUTTON_FIELD)
    new_button = Button(label=NEW_LABEL, id=NEW_BUTTON_FIELD)
    update_button = Button(label=UPDATE_LABEL, id=UPDATE_BUTTON_FIELD)


    def compose(self):
        # Local Monero daemon deployment form
        INTRO = "This screen provides a form for creating a new " \
            f"[bold cyan]{MONEROD_LABEL}[/] deployment."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Horizontal(
                        Label(INSTANCE_LABEL, classes=FORM_LABEL_FIELD),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(IN_PEERS_LABEL, classes=FORM_LABEL_FIELD),
                        self.in_peers_input),
                    Horizontal(
                        Label(OUT_PEERS_LABEL, classes=FORM_LABEL_FIELD),
                        self.out_peers_input),
                    Horizontal(
                        Label(P2P_BIND_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.p2p_bind_port_input),
                    Horizontal(
                        Label(RPC_BIND_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.rpc_bind_port_input),
                    Horizontal(
                        Label(ZMQ_PUB_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.zmq_pub_port_input),
                    Horizontal(
                        Label(ZMQ_RPC_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.zmq_rpc_port_input),
                    Horizontal(
                        Label(LOG_LEVEL_LABEL, classes=FORM_LABEL_FIELD),
                        self.log_level_input),
                    Horizontal(
                        Label(MAX_LOG_FILES_LABEL, classes=FORM_LABEL_FIELD),
                        self.max_log_files_input),
                    Horizontal(
                        Label(MAX_LOG_SIZE_LABEL, classes=FORM_LABEL_FIELD),
                        self.max_log_size_input),
                    Horizontal(
                        Label(PRIORITY_NODE_1_LABEL, classes=FORM_LABEL_FIELD),
                        self.priority_node_1_input),
                    Horizontal(
                        Label(PRIORITY_PORT_1_LABEL, classes=FORM_LABEL_FIELD),
                        self.priority_port_1_input),
                    Horizontal(
                        Label(PRIORITY_NODE_2_LABEL, classes=FORM_LABEL_FIELD),
                        self.priority_node_2_input),
                    Horizontal(
                        Label(PRIORITY_PORT_2_LABEL, classes=FORM_LABEL_FIELD),
                        self.priority_port_2_input),
                    Horizontal(
                        Label(CONFIG_FILE_LABLE, classes=FORM_LABEL_FIELD),
                        self.config_label),
                    Horizontal(
                        Label(DATA_DIR_LABEL, classes=FORM_LABEL_FIELD),
                        self.data_dir_label),
                    classes=FORM_16_FIELD),
                    
                    Vertical(
                        self.health_msgs,
                        classes=HEALTH_BOX_FIELD,
                    ),

                Vertical(
                    Horizontal(
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.disable_button,
                        self.delete_button,
                        classes=BUTTON_ROW_FIELD))),
                
            classes=PANE_BOX_FIELD)
        

    def set_data(self, monerod: MoneroD):
        self.monerod = monerod
        self.instance_input.value = monerod.instance()
        self.instance_label.update(monerod.instance())
        self.config_label.update(monerod.config_file())
        self.data_dir_label.update(monerod.data_dir())
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
            # This is an update operation
            self.remove_class(NEW_FIELD)
            self.add_class(UPDATE_FIELD)

            if monerod.enabled():
                self.remove_class(DISABLE_FIELD)
                self.add_class(ENABLE_FIELD)
            else:
                self.remove_class(ENABLE_FIELD)
                self.add_class(DISABLE_FIELD)

        else:
            # This is a new operation
            self.remove_class(UPDATE_FIELD)
            self.add_class(NEW_FIELD)

        self.health_msgs.update(gen_results_table(monerod.pop_msgs()))


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        self.monerod.instance(self.query_one("#instance_input", Input).value)
        self.monerod.in_peers(self.query_one("#in_peers_input", Input).value)
        self.monerod.out_peers(self.query_one("#out_peers_input", Input).value)
        self.monerod.p2p_bind_port(self.query_one("#p2p_bind_port_input", Input).value)
        self.monerod.rpc_bind_port(self.query_one("#rpc_bind_port_input", Input).value)
        self.monerod.zmq_pub_port(self.query_one("#zmq_pub_port_input", Input).value)
        self.monerod.zmq_rpc_port(self.query_one("#zmq_rpc_port_input", Input).value)
        self.monerod.log_level(self.query_one("#log_level_input", Input).value)
        self.monerod.max_log_files(self.query_one("#max_log_files_input", Input).value)
        self.monerod.max_log_size(self.query_one("#max_log_size_input", Input).value)
        self.monerod.priority_node_1(self.query_one("#priority_node_1_input", Input).value)
        self.monerod.priority_port_1(self.query_one("#priority_port_1_input", Input).value)
        self.monerod.priority_node_2(self.query_one("#priority_node_2_input", Input).value)
        self.monerod.priority_port_2(self.query_one("#priority_port_2_input", Input).value)

        if button_id == NEW_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                ELEMENT_FIELD: self.monerod
            }

        elif button_id == UPDATE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: UPDATE_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                ELEMENT_FIELD: self.monerod,
            }

        elif button_id == ENABLE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: ENABLE_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                ELEMENT_FIELD: self.monerod,
            }

        elif button_id == DISABLE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: DISABLE_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                ELEMENT_FIELD: self.monerod,
            }

        elif button_id == DELETE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: DELETE_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                ELEMENT_FIELD: self.monerod,
            }            

        self.app.post_message(Db4eMsg(self, form_data=form_data))                              
        # self.app.post_message(Db4eMsg(self, form_data=form_data))