"""
db4e/Panes/NewMonerodType.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from textual.widgets import Button, Label, MarkdownViewer, RadioButton, RadioSet, Static

from db4e.Constants.Labels import (
    DEPLOYMENTS_LABEL, MONEROD_LABEL, MONEROD_REMOTE_LABEL, MONEROD_SHORT_LABEL,
    PROCEED_LABEL
)
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DEPLOYMENT_MGR_FIELD, GET_NEW_REC_FIELD, 
    GET_NEW_REMOTE_REC_FIELD, MONEROD_FIELD, REMOTE_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD
)
from db4e.Messages.SubmitFormData import SubmitFormData

class NewMonerodType(Container):

    def compose(self):
        INTRO = f"Welcome to the {MONEROD_LABEL} {DEPLOYMENTS_LABEL} screen. "
        INTRO += f"On this screen you can choose to deploy a *local* or *remote* "
        INTRO += f"{MONEROD_LABEL} {DEPLOYMENTS_LABEL}.\n\nA *local* {MONEROD_LABEL} "
        INTRO += f"will run on this machine. Remote deployments connect to a "
        INTRO += f"{MONEROD_LABEL} running on a remote machine."
       
        yield Vertical(
            Vertical(
                Label(INTRO, classes="form_intro")),
            
            Vertical(
                RadioSet(
                    RadioButton(MONEROD_LABEL, id="local", classes="radio_button_type", value=True),
                    RadioButton(MONEROD_REMOTE_LABEL, id="remote", classes="radio_button_type"),
                    ),
                classes="radio_set"),

            Button(label=PROCEED_LABEL, classes="update_button"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected.id == "remote":
            form_data = {
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: GET_NEW_REMOTE_REC_FIELD,
                COMPONENT_FIELD: MONEROD_FIELD,
                REMOTE_FIELD: True
            }
        else:
            form_data = {
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: GET_NEW_REC_FIELD,
                COMPONENT_FIELD: MONEROD_FIELD,
                REMOTE_FIELD: False
            }
        self.app.post_message(SubmitFormData(self, form_data))