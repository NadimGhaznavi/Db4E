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
from db4e.Constants.Fields import DField, DMod, DElem, Method
from db4e.Constants.Buttons import DButton
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
                Label(INTRO, classes=Form.INTRO.value),
                
                Vertical(
                    RadioSet(
                        RadioButton(
                            "Local " + DLabel.MONEROD, 
                            classes=Form.RADIO_BUTTON_TYPE.value, value=True),
                        RadioButton(
                            DLabel.MONEROD_REMOTE, id="remote", 
                            classes=Form.RADIO_BUTTON_TYPE.value),
                        id="type_radioset", classes=Form.RADIO_SET.value,
                        )),

                Button(label=DLabel.PROCEED, id=DButton.PROCEED)),
                classes=Form.PANE_BOX.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected.id == DField.REMOTE:
            form_data = {
                DField.TO_MODULE: DMod.OPS_MGR,
                DField.TO_METHOD: Method.GET_NEW,
                DField.ELEMENT_TYPE: DElem.MONEROD_REMOTE,
                DField.REMOTE: True
            }
        else:
            form_data = {
                DField.TO_MODULE: DMod.OPS_MGR,
                DField.TO_METHOD: Method.GET_NEW,
                DField.ELEMENT_TYPE: DElem.MONEROD,
                DField.REMOTE: False
            }
        self.app.post_message(Db4eMsg(self, form_data))