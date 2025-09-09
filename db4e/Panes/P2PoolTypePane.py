"""
db4e/Panes/P2PoolTypePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Button, RadioButton, RadioSet, Label

from db4e.Constants.Labels import DLabel
from db4e.Constants.Fields import (
    REMOTE_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD, GET_NEW_FIELD)
from db4e.Constants.Fields import DField, DMod, DElem
from db4e.Constants.Buttons import (PROCEED_BUTTON_FIELD)
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.Form import Form

color = "#9cae41"
hi = "cyan"

class P2PoolTypePane(Container):

    def compose(self):
        INTRO = f"Welcome to the new [b {hi}]{DLabel.P2POOL}[/] screen. Use to create " \
            f"a new [{hi}]local[/] or [{hi}]remote[/] {DLabel.P2POOL} deployment.\n\n" \
            f"A [{hi}]local {DLabel.P2POOL}[/] deployment will setup a " \
            f"[{hi}]{DLabel.P2POOL}[/] on this machine. [{hi}]Remote[/] deployments " \
            f"connect to a [{hi}]{DLabel.P2POOL}[/] running on a remote machine."
                    
        yield Vertical (
            ScrollableContainer(
                Label(INTRO, classes="form_intro"),

                Vertical(
                    RadioSet(
                        RadioButton("Local " + DLabel.P2POOL, id="local", value=True),
                        RadioButton(DLabel.P2POOL_REMOTE, id="remote"),
                        id="type_radioset", classes="radio_set",
                    )),

                Button(label=DLabel.PROCEED, id=PROCEED_BUTTON_FIELD)),
                classes=Form.PANE_BOX)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected and selected.id == "remote":
            form_data = {
                TO_MODULE_FIELD: DMod.OPS_MGR,
                TO_METHOD_FIELD: GET_NEW_FIELD,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                REMOTE_FIELD: True
            }
        else:
            form_data = {
                TO_MODULE_FIELD: DMod.OPS_MGR,
                TO_METHOD_FIELD: GET_NEW_FIELD,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                REMOTE_FIELD: False
            }


        self.app.post_message(Db4eMsg(self, form_data))