"""
db4e/Panes/MoneroDTypePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import (Button, Label, RadioButton, RadioSet)
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm
from db4e.Constants.DField import DField
from db4e.Constants.DModule import DModule
from db4e.Constants.DElem import DElem
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DButton import DButton
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
                Label(INTRO, classes=DForm.INTRO),
                
                Vertical(
                    RadioSet(
                        RadioButton(
                            "Local " + DLabel.MONEROD, 
                            classes=DForm.RADIO_BUTTON_TYPE, value=True),
                        RadioButton(
                            DLabel.MONEROD_REMOTE, id="remote", 
                            classes=DForm.RADIO_BUTTON_TYPE),
                        id="type_radioset", classes=DForm.RADIO_SET,
                        )),

                Button(label=DLabel.PROCEED, id=DButton.PROCEED)),
                classes=DForm.PANE_BOX)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected.id == DField.REMOTE:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.GET_NEW,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                DField.REMOTE: True
            }
        else:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.GET_NEW,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.REMOTE: False
            }
        self.app.post_message(Db4eMsg(self, form_data))