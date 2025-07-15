"""
db4e/Panes/NewP2Pool.py

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
    IP_ADDR_FIELD, P2POOL_FIELD, REMOTE_FIELD, STRATUM_PORT_FIELD, 
    TO_MODULE_FIELD, TO_METHOD_FIELD,
)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, IP_ADDR_LABEL, P2POOL_LABEL, P2POOL_REMOTE_LABEL, 
    PROCEED_LABEL, STRATUM_PORT_LABEL
)
from db4e.Constants.Defaults import (
    STRATUM_PORT_DEFAULT
)

class NewRemoteP2Pool(Container):

    instance_input = Input(id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True)
    ip_addr_input = Input(id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True)
    stratum_port_input = Input(id="stratum_port_input", restrict=f"[0-9]*", compact=True)
    remote_flag = bool

    def compose(self):

        # Remote P2Pool daemon deployment form
        STATIC_CONTENT = "This screen provides a form for creating a new "
        STATIC_CONTENT += f"{P2POOL_REMOTE_LABEL} deployment."

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
                Button(label=PROCEED_LABEL, id="proceed_button"),
                id="buttons")) 

    def reset_data(self):
        self.instance_input.value = ""
        self.ip_addr_input.value = ""
        self.stratum_port_input.value = str(STRATUM_PORT_DEFAULT)

    def set_data(self, rec):
        self.remote_flag = rec.get(REMOTE_FIELD)
        self.stratum_port_input.value = str(STRATUM_PORT_DEFAULT)

    def get_remote(self):
        return self.remote_flag
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        form_data = {
            COMPONENT_FIELD: P2POOL_FIELD,
            TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
            TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
            REMOTE_FIELD: True,
            INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
            IP_ADDR_FIELD: self.query_one("#ip_addr_input", Input).value,
            STRATUM_PORT_FIELD: self.query_one("#stratum_port_input", Input).value,
        }
        self.app.post_message(SubmitFormData(self, form_data=form_data))