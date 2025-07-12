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

STATIC_CONTENT = f"This screen allows you to view and edit the deployment "
STATIC_CONTENT += f"settings for the {P2POOL_REMOTE_LABEL} deployment."

class P2PoolRemote(Container):

    def set_data(self, depl_config):

        instance = depl_config[INSTANCE_FIELD]
        ip_addr = depl_config[IP_ADDR_FIELD]
        stratum_port = depl_config[STRATUM_PORT_FIELD]

        md = Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(INSTANCE_LABEL, id="p2pool_remote_instance_label"),
                    Input(id="p2pool_remote_instance",
                          restrict=f"[a-zA-Z0-9_\-]*", value=instance, compact=True)),
                Horizontal(
                    Label(IP_ADDR_LABEL, id="p2pool_remote_ip_addr_label"),
                    Input(id="p2pool_remote_ip_addr",
                          restrict=f"[a-z0-9._\-]*", value=ip_addr, compact=True)),
                Horizontal(
                    Label(STRATUM_PORT_LABEL, id="p2pool_remote_stratum_port_label"),
                    Input(id="p2pool_remote_stratum_port",
                          restrict=f"[0-9]*", value=str(stratum_port), compact=True)),
                id="p2pool_remote_update_form"),

            Input(id="p2pool_remote_orig_instance", value=instance, classes="hidden"),

            Horizontal(
                Button(label=UPDATE_LABEL, id="p2pool_remote_update_button"),
                Button(label=DELETE_LABEL, id="p2pool_remote_delete_button")
            ))
        self.remove_children()
        self.mount(md)
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        button_id = event.button.id
        if button_id == "p2pool_remote_update_button":
            form_data = {
                COMPONENT_FIELD: P2POOL_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
                FORM_DATA_FIELD: True,
                REMOTE_FIELD: True,
                INSTANCE_FIELD: self.query_one("#p2pool_remote_instance", Input).value,
                ORIG_INSTANCE_FIELD: self.query_one("#p2pool_remote_orig_instance", Input).value,
                IP_ADDR_FIELD: self.query_one("#p2pool_remote_ip_addr", Input).value,
                STRATUM_PORT_FIELD: self.query_one("#p2pool_remote_stratum_port", Input).value,
            }
        else:
            form_data = {
                COMPONENT_FIELD: P2POOL_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: DELETE_DEPLOYMENT_FIELD,
                COMPONENT_FIELD: P2POOL_FIELD,
                INSTANCE_FIELD: self.query_one("#p2pool_remote_instance", Input).value,
            }            

        self.app.post_message(SubmitFormData(self, form_data=form_data))