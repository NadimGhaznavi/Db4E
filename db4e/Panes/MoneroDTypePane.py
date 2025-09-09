"""
db4e/Panes/MoneroDTypePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer
from textual.app import ComposeResult
from textual.widgets import Button, Label, MarkdownViewer, RadioButton, RadioSet, Static

from db4e.Constants.Labels import DLabel
from db4e.Constants.Form import Form
from db4e.Constants.Fields import (
    GET_NEW_FIELD, RADIO_BUTTON_TYPE_FIELD,
    REMOTE_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, RADIO_SET_FIELD)
from db4e.Constants.Fields import DField, DMod, DElem
from db4e.Constants.Buttons import (PROCEED_BUTTON_FIELD)
from db4e.Messages.Db4eMsg import Db4eMsg

hi = "cyan"

class MoneroDTypePane(Container):

    def compose(self):
        INTRO = f"Welcome to the new [b {hi}]{DLabel.MONEROD}[/] screen. Use to create " \
            f"a new [{hi}]local[/] or [{hi}]remote[/] {DLabel.MONEROD} deployment.\n\n" \
            f"A [{hi}]local {DLabel.MONEROD}[/] deployment will setup a " \
            f"[{hi}]{DLabel.MONEROD}[/] on this machine. [{hi}]Remote[/] deployments " \
            f"connect to a [{hi}]{DLabel.MONEROD}[/] running on a remote machine."
       
        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=Form.INTRO),
                
                Vertical(
                    RadioSet(
                        RadioButton("Local " + DLabel.MONEROD, classes=RADIO_BUTTON_TYPE_FIELD, value=True),
                        RadioButton(DLabel.MONEROD_REMOTE, id="remote", classes=RADIO_BUTTON_TYPE_FIELD),
                        id="type_radioset", classes=RADIO_SET_FIELD,
                        )),

                Button(label=DLabel.PROCEED, id=PROCEED_BUTTON_FIELD)),
                classes=Form.PANE_BOX)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected.id == REMOTE_FIELD:
            form_data = {
                TO_MODULE_FIELD: DMod.OPS_MGR,
                TO_METHOD_FIELD: GET_NEW_FIELD,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                REMOTE_FIELD: True
            }
        else:
            form_data = {
                TO_MODULE_FIELD: DMod.OPS_MGR,
                TO_METHOD_FIELD: GET_NEW_FIELD,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                REMOTE_FIELD: False
            }
        self.app.post_message(Db4eMsg(self, form_data))