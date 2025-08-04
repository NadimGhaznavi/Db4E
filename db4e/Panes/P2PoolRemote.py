"""
db4e/Panes/P2PoolRemote.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from rich import box
from rich.table import Table

from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, MarkdownViewer, Button, Input, Static

from db4e.Modules.Helper import gen_results_table, get_component_value
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, BUTTON_ROW_FIELD, ELEMENT_TYPE_FIELD,
    DELETE_BUTTON_FIELD, DELETE_DEPLOYMENT_FIELD, FORM_3_FIELD, FORM_DATA_FIELD,
    FORM_INPUT_30_FIELD, FORM_INTRO_FIELD, FORM_LABEL_FIELD, GREEN_BUTTON_FIELD,
    HEALTH_BOX_FIELD, HEALTH_MSGS_FIELD, INSTANCE_FIELD, IP_ADDR_FIELD,
    ORIG_INSTANCE_FIELD, OPS_MGR_FIELD, P2POOL_REMOTE_FIELD,
    DEPLOYMENT_MGR_FIELD, PANE_BOX_FIELD,
    RED_BUTTON_FIELD, STRATUM_PORT_FIELD, TO_METHOD_FIELD,
    TO_MODULE_FIELD, UPDATE_BUTTON_FIELD, UPDATE_DEPLOYMENT_FIELD)
from db4e.Constants.Labels import (
    DELETE_LABEL, UPDATE_LABEL, INSTANCE_LABEL, IP_ADDR_LABEL,
    P2POOL_REMOTE_LABEL, STRATUM_PORT_LABEL)

class P2PoolRemote(Container):

    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True, 
        classes=FORM_INPUT_30_FIELD)
    ip_addr_input = Input(
        id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    stratum_port_input = Input(
        id="stratum_port_input", restrict=f"[0-9]*", compact=True, 
        classes=FORM_INPUT_30_FIELD)
    health_msgs = Static()

    def compose(self):
        # Remote P2Pool deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{P2POOL_REMOTE_LABEL}[/] deployment here."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Horizontal(
                        Label(INSTANCE_LABEL, classes=FORM_LABEL_FIELD),
                        self.instance_input),
                    Horizontal(
                        Label(IP_ADDR_LABEL, classes=FORM_LABEL_FIELD),
                        self.ip_addr_input),
                    Horizontal(
                        Label(STRATUM_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.stratum_port_input),
                    classes=FORM_3_FIELD),

                Vertical(
                    self.health_msgs,
                    classes=HEALTH_BOX_FIELD,
                ),

                Horizontal(
                    Button(label=UPDATE_LABEL, id=UPDATE_BUTTON_FIELD, 
                           classes=GREEN_BUTTON_FIELD),
                    Button(label=DELETE_LABEL, id=DELETE_BUTTON_FIELD, 
                           classes=RED_BUTTON_FIELD),
                    classes=BUTTON_ROW_FIELD
                ),
        
                classes=PANE_BOX_FIELD))

    def set_data(self, rec):
        self.orig_instance = get_component_value(rec, INSTANCE_FIELD)
        self.instance_input.value = get_component_value(rec, INSTANCE_FIELD)
        self.ip_addr_input.value = get_component_value(rec, IP_ADDR_FIELD)
        self.stratum_port_input.value = str(get_component_value(rec, STRATUM_PORT_FIELD))
        self.health_msgs.update(gen_results_table(rec[HEALTH_MSGS_FIELD]))
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == UPDATE_BUTTON_FIELD:
                
            if len(self.orig_instance) > 0:
                # There was an original instance, so this is an update            
                form_data = {
                    ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
                    FORM_DATA_FIELD: True,
                    ORIG_INSTANCE_FIELD: self.orig_instance,
                    INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
                    IP_ADDR_FIELD: self.query_one("#ip_addr_input", Input).value,
                    STRATUM_PORT_FIELD: self.query_one("#stratum_port_input", Input).value,
                }
            else:
                # No original instance, this is a new deployment
                form_data = {
                    ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
                    FORM_DATA_FIELD: True,
                    INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
                    IP_ADDR_FIELD: self.query_one("#ip_addr_input", Input).value,
                    STRATUM_PORT_FIELD: self.query_one("#stratum_port_input", Input).value,
                }

        elif button_id == DELETE_BUTTON_FIELD:
            form_data = {
                ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: DELETE_DEPLOYMENT_FIELD,
                FORM_DATA_FIELD: True,
                INSTANCE_FIELD: self.orig_instance
            }
        else:
            raise ValueError(f"No handler for {button_id}")
        self.app.post_message(Db4eMsg(self, form_data=form_data))
        self.app.post_message(RefreshNavPane(self))
        