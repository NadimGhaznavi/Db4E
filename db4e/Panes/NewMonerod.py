"""
db4e/Panes/NewMonerod.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Input, Button, MarkdownViewer

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, COMPONENT_FIELD, DEPLOYMENT_MGR_FIELD, INSTANCE_FIELD, 
    IP_ADDR_FIELD, LOCAL_FIELD, MONEROD_FIELD, REMOTE_FIELD, RPC_BIND_PORT_FIELD, 
    TO_MODULE_FIELD, TO_METHOD_FIELD, ZMQ_PUB_PORT_FIELD,
)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, IP_ADDR_LABEL, MONEROD_LABEL, MONEROD_REMOTE_LABEL, PROCEED_LABEL, 
    RPC_BIND_PORT_LABEL, ZMQ_PUB_PORT_LABEL
)
from db4e.Constants.Defaults import (
    RPC_BIND_PORT_DEFAULT, ZMQ_PUB_PORT_DEFAULT
)


class NewMonerod(Container):

    def set_data(self, rec):
        self.mount(Label(str(rec)))

        if rec.get(REMOTE_FIELD):
            # Remote Monero daemon deployment form
            STATIC_CONTENT = "This screen provides a form for creating a new "
            STATIC_CONTENT += f"{MONEROD_REMOTE_LABEL} deployment."

            md = Vertical(
                MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

                Vertical(
                    Horizontal(
                        Label(INSTANCE_LABEL, id="new_monerod_instance_label"),
                        Input(id="new_monerod_instance_input", 
                            restrict=f"[a-zA-Z0-9_\-]*", compact=True)),
                    Horizontal(
                        Label(IP_ADDR_LABEL, id="new_monerod_ip_addr_label"),
                        Input(id="new_monerod_ip_addr_input", 
                            restrict=f"[a-z0-9._\-]*", compact=True)),
                    Horizontal(
                        Label(RPC_BIND_PORT_LABEL, id="new_monerod_rpc_bind_port_label"),
                        Input(id="new_monerod_rpc_bind_port_input", 
                            restrict=f"[0-9]*", value=str(RPC_BIND_PORT_DEFAULT), compact=True)),
                    Horizontal(
                        Label(ZMQ_PUB_PORT_LABEL, id="new_monerd_zmq_pub_port_label"),
                        Input(id="new_monerod_zmq_pub_port_input",
                            restrict=f"[0-9]*", value=str(ZMQ_PUB_PORT_DEFAULT), compact=True)),    
                    id="new_monerod_form"),

                Horizontal(
                    Button(label=PROCEED_LABEL, id="new_monerod_proceed_button"),
                    id="new_monerod_buttons"),
                Input(id="new_monerod_type", value=REMOTE_FIELD, classes="hidden"))
            
            self.remove_children()
            self.mount(md)

        else:
            # Local Monero daemon deployment form
            STATIC_CONTENT = "This screen provides a form for creating a new "
            STATIC_CONTENT += f"{MONEROD_LABEL} deployment."
            md = Vertical(
                MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

                Vertical(
                    Label('🚧 Coming Soon 🚧')
                ),

                Horizontal(
                    Input(id="new_monerod_type", value=LOCAL_FIELD, classes="hidden")
                )   
            )
            
            self.remove_children()
            self.mount(md)


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if self.query_one("#new_monerod_type", Input).value == REMOTE_FIELD:
            remote_value = True
        else:
            remote_value = False
        form_data = {
            COMPONENT_FIELD: MONEROD_FIELD,
            TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
            TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
            REMOTE_FIELD: remote_value,
            INSTANCE_FIELD: self.query_one("#new_monerod_instance_input", Input).value,
            IP_ADDR_FIELD: self.query_one("#new_monerod_ip_addr_input", Input).value,
            RPC_BIND_PORT_FIELD: self.query_one("#new_monerod_rpc_bind_port_input", Input).value,
            ZMQ_PUB_PORT_FIELD: self.query_one("#new_monerod_zmq_pub_port_input", Input).value,
        }
        self.app.post_message(SubmitFormData(self, form_data=form_data))