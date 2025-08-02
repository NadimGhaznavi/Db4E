"""
db4e/Panes/MonerodType.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer
from textual.app import ComposeResult
from textual.widgets import Button, Label, MarkdownViewer, RadioButton, RadioSet, Static

from db4e.Constants.Labels import (
    MONEROD_LABEL, MONEROD_REMOTE_LABEL, MONEROD_SHORT_LABEL,
    PROCEED_LABEL
)
from db4e.Constants.Fields import (
    FORM_INTRO_FIELD, GET_NEW_REC_FIELD,
    MONEROD_FIELD, OPS_MGR_FIELD, PANE_BOX_FIELD, RADIO_BUTTON_TYPE_FIELD,
    REMOTE_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, GREEN_BUTTON_FIELD,
    RADIO_SET_FIELD, ELEMENT_TYPE_FIELD, MONEROD_REMOTE_FIELD
)
from db4e.Messages.Db4eMsg import Db4eMsg

color = "#9cae41"
hi = "cyan"

class MonerodType(Container):

    def compose(self):
        INTRO = f"Welcome to the new [b {hi}]{MONEROD_LABEL}[/] screen. Use to create " \
            f"a new [{hi}]local[/] or [{hi}]remote[/] {MONEROD_LABEL} deployment.\n\n" \
            f"A [{hi}]local {MONEROD_LABEL}[/] deployment will setup a " \
            f"[{hi}]{MONEROD_LABEL}[/] on this machine. [{hi}]Remote[/] deployments " \
            f"connect to a [{hi}]{MONEROD_LABEL}[/] running on a remote machine."
       
        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),
                
                Vertical(
                    RadioSet(
                        RadioButton("Local " + MONEROD_LABEL, classes=RADIO_BUTTON_TYPE_FIELD, value=True),
                        RadioButton(MONEROD_REMOTE_LABEL, id="remote", classes=RADIO_BUTTON_TYPE_FIELD),
                        id="type_radioset", classes=RADIO_SET_FIELD,
                        )),

                Button(label=PROCEED_LABEL, classes=GREEN_BUTTON_FIELD)),
                classes=PANE_BOX_FIELD)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected.id == REMOTE_FIELD:
            form_data = {
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: GET_NEW_REC_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                REMOTE_FIELD: True
            }
        else:
            form_data = {
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: GET_NEW_REC_FIELD,
                ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                REMOTE_FIELD: False
            }
        self.app.post_message(Db4eMsg(self, form_data))