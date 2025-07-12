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

class NewP2Pool(Container):

    def set_data(self, rec):
        self.mount(Label(str(rec)))

        if rec.get(REMOTE_FIELD):
            # Remote P2Pool daemon deployment form
            STATIC_CONTENT = "This screen provides a form for creating a new "
            STATIC_CONTENT += f"{P2POOL_REMOTE_LABEL} deployment."

            md = Vertical(
                MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

                Vertical(
                    Horizontal(
                        Label(INSTANCE_LABEL, id="new_p2pool_instance_label"),
                        Input(id="new_p2pool_instance_input", 
                            restrict=f"[a-zA-Z0-9_\-]*", compact=True)),
                    Horizontal(
                        Label(IP_ADDR_LABEL, id="new_p2pool_ip_addr_label"),
                        Input(id="new_p2pool_ip_addr_input", 
                            restrict=f"[a-z0-9._\-]*", compact=True)),
                    Horizontal(
                        Label(STRATUM_PORT_LABEL, id="new_p2pool_stratum_port_label"),
                        Input(id="new_p2pool_stratum_port_input", 
                            restrict=f"[0-9]*", value=str(STRATUM_PORT_DEFAULT), compact=True)),
                    id="new_p2pool_type_form"),

                Horizontal(
                    Button(label=PROCEED_LABEL, id="new_p2pool_proceed_button"),
                    id="new_p2pool_buttons"),
                Input(id="p2pool_remote_flag", value="True", classes="hidden"))
            
            self.remove_children()
            self.mount(md)

        else:
            # Local P2Pool daemon deployment form
            STATIC_CONTENT = "This screen provides a form for creating a new "
            STATIC_CONTENT += f"{P2POOL_LABEL} deployment."
            md = Vertical(
                MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),
                Label('🚧 Coming Soon 🚧')
            )
            self.remove_children()
            self.mount(md)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        form_data = {
            COMPONENT_FIELD: P2POOL_FIELD,
            TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
            TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
            REMOTE_FIELD: self.query_one("#p2pool_remote_flag", Input).value,
            INSTANCE_FIELD: self.query_one("#new_p2pool_instance_input", Input).value,
            IP_ADDR_FIELD: self.query_one("#new_p2pool_ip_addr_input", Input).value,
            STRATUM_PORT_FIELD: self.query_one("#new_p2pool_stratum_port_input", Input).value,
        }
        self.app.post_message(SubmitFormData(self, form_data=form_data))