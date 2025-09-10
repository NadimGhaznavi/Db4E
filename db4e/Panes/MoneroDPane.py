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
from db4e.Constants.Fields import DField, DElem, DMod, Method
from db4e.Constants.Labels import DLabel
from db4e.Constants.Form import Form
from db4e.Constants.Jobs import DJob
from db4e.Constants.Buttons import DButton

color = "#9cae41"
hi = "#d7e556"

class MoneroDPane(Container):

    config_label = Label("", classes=Form.STATIC.value)
    any_ip_label = Label("", classes=Form.STATIC.value)
    data_dir_label = Label("", classes=Form.STATIC.value)
    instance_label = Label("", id="instance_label",classes=Form.STATIC.value)

    in_peers_input = Input(
        id="in_peers_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_30.value)
    instance_input = Input(
        compact=True, id="instance_input", restrict=f"[a-zA-Z0-9_\-]*",
        classes=Form.INPUT_30.value)
    log_level_input = Input(
        id="log_level_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_30.value)
    max_log_files_input = Input(
        id="max_log_files_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_30.value)
    max_log_size_input = Input(
        id="max_log_size_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_30.value)
    out_peers_input = Input(
        id="out_peers_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_30.value)
    p2p_bind_port_input = Input(
        id="p2p_bind_port_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_30.value)
    primary_server_checkbox = Checkbox(
        "", compact=True, id="primary_server_checkbox")
    priority_node_1_input = Input(
        id="priority_node_1_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=Form.INPUT_30.value)
    priority_port_1_input = Input(
        id="priority_port_1_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=Form.INPUT_30.value)
    priority_node_2_input = Input(
        id="priority_node_2_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_30.value)
    priority_port_2_input = Input(
        id="priority_port_2_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_30.value)
    rpc_bind_port_input = Input(
        compact=True, id="rpc_bind_port_input", restrict=f"[0-9]*",
        classes=Form.INPUT_30.value)
    zmq_pub_port_input = Input(
        compact=True, id="zmq_pub_port_input", restrict=f"[0-9]*",
        classes=Form.INPUT_30.value)
    zmq_rpc_port_input = Input(
        compact=True, id="zmq_rpc_port_input", restrict=f"[0-9]*",
        classes=Form.INPUT_30.value)

    health_msgs = Label()

    delete_button = Button(label=DLabel.DELETE, id=DButton.DELETE)
    disable_button = Button(label=DLabel.DISABLE, id=DButton.DISABLE)
    enable_button = Button(label=DLabel.ENABLE, id=DButton.ENABLE)
    new_button = Button(label=DLabel.NEW, id=DButton.NEW)
    update_button = Button(label=DLabel.UPDATE, id=DButton.UPDATE)


    def compose(self):
        # Local Monero daemon deployment form
        INTRO = "This screen provides a form for creating a new " \
            f"[bold cyan]{DLabel.MONEROD}[/] deployment."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=Form.INTRO.value),

                Vertical(
                    Horizontal(
                        Label(DLabel.PRIMARY_SERVER, classes=Form.FORM_LABEL.value),
                        self.primary_server_checkbox),
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=Form.FORM_LABEL.value),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.IN_PEERS, classes=Form.FORM_LABEL.value),
                        self.in_peers_input),
                    Horizontal(
                        Label(DLabel.OUT_PEERS, classes=Form.FORM_LABEL.value),
                        self.out_peers_input),
                    Horizontal(
                        Label(DLabel.P2P_BIND_PORT, classes=Form.FORM_LABEL.value),
                        self.p2p_bind_port_input),
                    Horizontal(
                        Label(DLabel.RPC_BIND_PORT, classes=Form.FORM_LABEL.value),
                        self.rpc_bind_port_input),
                    Horizontal(
                        Label(DLabel.ZMQ_PUB_PORT, classes=Form.FORM_LABEL.value),
                        self.zmq_pub_port_input),
                    Horizontal(
                        Label(DLabel.ZMQ_RPC_PORT, classes=Form.FORM_LABEL.value),
                        self.zmq_rpc_port_input),
                    Horizontal(
                        Label(DLabel.LOG_LEVEL, classes=Form.FORM_LABEL.value),
                        self.log_level_input),
                    Horizontal(
                        Label(DLabel.MAX_LOG_FILES, classes=Form.FORM_LABEL.value),
                        self.max_log_files_input),
                    Horizontal(
                        Label(DLabel.MAX_LOG_SIZE, classes=Form.FORM_LABEL.value),
                        self.max_log_size_input),
                    Horizontal(
                        Label(DLabel.PRIORITY_NODE_1, classes=Form.FORM_LABEL.value),
                        self.priority_node_1_input),
                    Horizontal(
                        Label(DLabel.PRIORITY_PORT_1, classes=Form.FORM_LABEL.value),
                        self.priority_port_1_input),
                    Horizontal(
                        Label(DLabel.PRIORITY_NODE_2, classes=Form.FORM_LABEL.value),
                        self.priority_node_2_input),
                    Horizontal(
                        Label(DLabel.PRIORITY_PORT_2, classes=Form.FORM_LABEL.value),
                        self.priority_port_2_input),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=Form.FORM_LABEL.value),
                        self.config_label),
                    Horizontal(
                        Label(DLabel.DATA_DIR, classes=Form.FORM_LABEL.value),
                        self.data_dir_label),
                    classes=Form.FORM_17.value),
                    
                    Vertical(
                        self.health_msgs,
                        classes=Form.HEALTH_BOX.value,
                    ),

                Vertical(
                    Horizontal(
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.disable_button,
                        self.delete_button,
                        classes=Form.BUTTON_ROW.value))),
                
            classes=Form.PANE_BOX.value)
        

    def set_data(self, monerod: MoneroD):
        self.monerod = monerod
        self.instance_input.value = monerod.instance()
        self.instance_label.update(monerod.instance())
        self.config_label.update(monerod.config_file())
        self.data_dir_label.update(monerod.data_dir())
        self.in_peers_input.value = str(monerod.in_peers())
        self.out_peers_input.value = str(monerod.out_peers())
        self.primary_server_checkbox.value = monerod.primary_server()
        self.p2p_bind_port_input.value = str(monerod.p2p_bind_port())
        self.rpc_bind_port_input.value = str(monerod.rpc_bind_port())
        self.zmq_pub_port_input.value = str(monerod.zmq_pub_port())
        self.zmq_rpc_port_input.value = str(monerod.zmq_rpc_port())
        self.log_level_input.value = str(monerod.log_level())
        self.max_log_files_input.value = str(monerod.max_log_files())
        self.max_log_size_input.value = str(monerod.max_log_size())
        self.primary_server_checkbox.value = monerod.primary_server()
        self.priority_node_1_input.value = str(monerod.priority_node_1())
        self.priority_port_1_input.value = str(monerod.priority_port_1())
        self.priority_node_2_input.value = str(monerod.priority_node_2())
        self.priority_port_2_input.value = str(monerod.priority_port_2())

        # Configure button visibility
        if monerod.instance():
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
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.health_msgs.update(gen_results_table(monerod.pop_msgs()))


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        self.monerod.instance(self.query_one("#instance_input", Input).value)
        self.monerod.in_peers(self.query_one("#in_peers_input", Input).value)
        self.monerod.out_peers(self.query_one("#out_peers_input", Input).value)
        self.monerod.p2p_bind_port(self.query_one("#p2p_bind_port_input", Input).value)
        self.monerod.primary_server(self.query_one("#primary_server_checkbox", Checkbox).value)
        self.monerod.rpc_bind_port(self.query_one("#rpc_bind_port_input", Input).value)
        self.monerod.zmq_pub_port(self.query_one("#zmq_pub_port_input", Input).value)
        self.monerod.zmq_rpc_port(self.query_one("#zmq_rpc_port_input", Input).value)
        self.monerod.log_level(self.query_one("#log_level_input", Input).value)
        self.monerod.max_log_files(self.query_one("#max_log_files_input", Input).value)
        self.monerod.max_log_size(self.query_one("#max_log_size_input", Input).value)
        self.monerod.primary_server(self.query_one("#primary_server_checkbox", Checkbox).value)
        self.monerod.priority_node_1(self.query_one("#priority_node_1_input", Input).value)
        self.monerod.priority_port_1(self.query_one("#priority_port_1_input", Input).value)
        self.monerod.priority_node_2(self.query_one("#priority_node_2_input", Input).value)
        self.monerod.priority_port_2(self.query_one("#priority_port_2_input", Input).value)

        if button_id == DButton.NEW:
            form_data = {
                DField.TO_MODULE: DMod.OPS_MGR,
                DField.TO_METHOD: Method.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod
            }

        elif button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.UPDATE,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.ENABLE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.ENABLE,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.DISABLE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.DISABLE,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }

        elif button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.DELETE,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.ELEMENT: self.monerod,
            }            

        self.app.post_message(Db4eMsg(self, form_data=form_data))                              
        # self.app.post_message(Db4eMsg(self, form_data=form_data))