"""
db4e/Panes/P2PoolType.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Button, RadioButton, RadioSet, Label

from db4e.Constants.Labels import (
    DEPLOYMENTS_LABEL, P2POOL_LABEL, P2POOL_REMOTE_LABEL,
    PROCEED_LABEL
)
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DEPLOYMENT_MGR_FIELD, GET_NEW_REC_FIELD, GET_NEW_REMOTE_REC_FIELD, 
    GREEN_BUTTON_FIELD, P2POOL_FIELD, PANE_BOX_FIELD, REMOTE_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD
)
from db4e.Messages.SubmitFormData import SubmitFormData


class P2PoolType(Container):

    def compose(self):
        INTRO = f"Welcome to the [cyan bold]{P2POOL_LABEL} {DEPLOYMENTS_LABEL}[/] screen. " \
            f"On this screen you can choose to deploy a [cyan]local[/] or [cyan]remote[/] " \
            f"{P2POOL_LABEL} {DEPLOYMENTS_LABEL}.\n\nA [cyan]local[/] {P2POOL_LABEL} " \
            f"will run on this machine. A [cyan]remote[/] {P2POOL_LABEL} " \
            f"{DEPLOYMENTS_LABEL} points at a {P2POOL_LABEL} that has already been setup."
                    
        yield Vertical (
            ScrollableContainer(
                Label(INTRO, classes="form_intro"),

                Vertical(
                    RadioSet(
                        RadioButton("Local " + P2POOL_LABEL, id="local", value=True),
                        RadioButton(P2POOL_REMOTE_LABEL, id="remote"),
                        id="type_radioset", classes="radio_set",
                    )),

                Button(label=PROCEED_LABEL, classes=GREEN_BUTTON_FIELD)),
                classes=PANE_BOX_FIELD)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected and selected.id == "remote":
            form_data = {
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: GET_NEW_REMOTE_REC_FIELD,
                COMPONENT_FIELD: P2POOL_FIELD,
                REMOTE_FIELD: True
            }
        else:
            form_data = {
                TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
                TO_METHOD_FIELD: GET_NEW_REC_FIELD,
                COMPONENT_FIELD: P2POOL_FIELD,
                REMOTE_FIELD: False
            }


        self.app.post_message(SubmitFormData(self, form_data))