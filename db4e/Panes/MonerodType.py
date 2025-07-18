"""
db4e/Panes/MonerodType.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer
from textual.app import ComposeResult
from textual.widgets import Button, Label, MarkdownViewer, RadioButton, RadioSet, Static

from db4e.Constants.Labels import (
    DEPLOYMENTS_LABEL, MONEROD_LABEL, MONEROD_REMOTE_LABEL, MONEROD_SHORT_LABEL,
    PROCEED_LABEL
)
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DEPLOYMENT_MGR_FIELD, FORM_INTRO_FIELD, GET_NEW_REC_FIELD, 
    GET_NEW_REMOTE_REC_FIELD, MONEROD_FIELD, PANE_BOX_FIELD, RADIO_BUTTON_TYPE_FIELD, 
    REMOTE_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD
)
from db4e.Messages.SubmitFormData import SubmitFormData

class MonerodType(Container):

    def compose(self):
        INTRO = f"Welcome to the [bold cyan]{MONEROD_LABEL} {DEPLOYMENTS_LABEL}[/] " \
            f"screen. On this screen you can choose to deploy a [cyan]local[/] or " \
            f"[cyan]remote[/] {MONEROD_LABEL} {DEPLOYMENTS_LABEL}.\n\nA [cyan]local[/] " \
            f"{MONEROD_LABEL} node will run on this machine. [cyan]Remote[/] " \
            f"deployments connect to a {MONEROD_LABEL} node that is already running " \
            f"on a remote machine."
       
        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),
                
                Vertical(
                    RadioSet(
                        RadioButton("Local " + MONEROD_LABEL, classes=RADIO_BUTTON_TYPE_FIELD, value=True),
                        RadioButton(MONEROD_REMOTE_LABEL, id="remote", classes=RADIO_BUTTON_TYPE_FIELD),
                        id="type_radioset", classes="radio_set",
                        )),

                Button(label=PROCEED_LABEL, classes="update_button")),
                classes=PANE_BOX_FIELD)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected.id == REMOTE_FIELD:
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