"""
db4e/Panes/P2PoolRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Label, MarkdownViewer, Button, Input

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DELETE_DEPLOYMENT_FIELD, DEPLOYMENT_MGR_FIELD, FORM_DATA_FIELD, 
    INSTANCE_FIELD, IP_ADDR_FIELD, P2POOL_FIELD, ORIG_INSTANCE_FIELD, REMOTE_FIELD, 
    STRATUM_PORT_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD, UPDATE_DEPLOYMENT_FIELD
)
from db4e.Constants.Labels import (
    DELETE_LABEL, INSTANCE_LABEL, IP_ADDR_LABEL, P2POOL_REMOTE_LABEL, 
    STRATUM_PORT_LABEL, UPDATE_LABEL
)

class P2PoolRemote(Container):

    instance_input = Input(id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True)
    ip_addr_input = Input(id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True)
    stratum_port_input = Input(id="stratum_port_input", restrict=f"[0-9]*", compact=True)

    def compose(self):
        # Remote P2Pool deployment form
        STATIC_CONTENT = f"This screen allows you to view and edit the deployment "
        STATIC_CONTENT += f"settings for the {P2POOL_REMOTE_LABEL} deployment."

        yield Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(INSTANCE_LABEL, id="instance_label"),
                    self.instance_input),
                Horizontal(
                    Label(IP_ADDR_LABEL, id="ip_addr_label"),
                    self.ip_addr_input),
                Horizontal(
                    Label(STRATUM_PORT_LABEL, id="stratum_port_label"),
                    self.stratum_port_input),
                id="p2pool_remote_form"),

            Horizontal(
                Button(label=UPDATE_LABEL, id="update_button"),
                Button(label=DELETE_LABEL, id="delete_button")
            ))

    def set_data(self, rec):

        self.orig_instance = rec[INSTANCE_FIELD]

        self.instance_input.value = rec[INSTANCE_FIELD]
        self.ip_addr_input.value = rec[IP_ADDR_FIELD]
        self.stratum_port_input.value = rec[STRATUM_PORT_FIELD]
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "update_button":
            form_data = {
                COMPONENT_FIELD: P2POOL_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
                FORM_DATA_FIELD: True,
                REMOTE_FIELD: True,
                ORIG_INSTANCE_FIELD: self.orig_instance,
                INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
                IP_ADDR_FIELD: self.query_one("#ip_addr_input", Input).value,
                STRATUM_PORT_FIELD: self.query_one("#stratum_port_input", Input).value,
            }
        else:
            form_data = {
                COMPONENT_FIELD: P2POOL_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: DELETE_DEPLOYMENT_FIELD,
                INSTANCE_FIELD: self.orig_instance
            }            

        self.app.post_message(SubmitFormData(self, form_data=form_data))