"""
db4e/Panes/P2PoolType.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Button, RadioButton, RadioSet, Label

from db4e.Constants.Labels import (
    P2POOL_LABEL, P2POOL_REMOTE_LABEL,PROCEED_LABEL)
from db4e.Constants.Fields import (
    COMPONENT_FIELD, OPS_MGR_FIELD, GET_NEW_REC_FIELD,
    GET_NEW_REMOTE_REC_FIELD, GREEN_BUTTON_FIELD, P2POOL_FIELD,
    PANE_BOX_FIELD, REMOTE_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD)
from db4e.Messages.SubmitFormData import SubmitFormData


class P2PoolType(Container):

    def compose(self):
        INTRO = f"Welcome to the new [yellow]{P2POOL_LABEL}[/] screen. Use to create " \
            f"a new [cyan]local[/] or [cyan]remote[/] {P2POOL_LABEL} deployment.\n\n" \
            f"A [cyan]local {P2POOL_LABEL}[/] deployment will setup a " \
            f"[cyan]{P2POOL_LABEL}[/] on this machine. [cyan]Remote[/] deployments " \
            f"connect to a [cyan]{P2POOL_LABEL}[/] running on a remote machine."
                    
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
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: GET_NEW_REMOTE_REC_FIELD,
                COMPONENT_FIELD: P2POOL_FIELD,
                REMOTE_FIELD: True
            }
        else:
            form_data = {
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: GET_NEW_REC_FIELD,
                COMPONENT_FIELD: P2POOL_FIELD,
                REMOTE_FIELD: False
            }


        self.app.post_message(SubmitFormData(self, form_data))