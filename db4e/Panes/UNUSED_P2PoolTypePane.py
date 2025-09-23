"""
db4e/Panes/P2PoolTypePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Button, RadioButton, RadioSet, Label

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DModule import DModule
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DButton import DButton
from db4e.Constants.DForm import DForm
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.DLabel import DLabel

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
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    RadioSet(
                        RadioButton("Local " + DLabel.P2POOL, id="local", value=True),
                        RadioButton(DLabel.P2POOL_REMOTE, id="remote"),
                        id="type_radioset", classes=DForm.RADIO_SET,
                    )),

                Button(label=DLabel.PROCEED, id=DButton.PROCEED)),
                classes=DForm.PANE_BOX)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected and selected.id == "remote":
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.GET_NEW,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                DField.REMOTE: True
            }
        else:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.GET_NEW,
                DField.ELEMENT_TYPE: DElem.P2POOL,
                DField.REMOTE: False
            }


        self.app.post_message(Db4eMsg(self, form_data))