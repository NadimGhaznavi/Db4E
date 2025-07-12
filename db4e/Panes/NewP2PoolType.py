"""
db4e/Panes/NewP2PoolType.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from textual.widgets import Button, Label, MarkdownViewer, RadioButton, RadioSet, Static

from db4e.Constants.Labels import (
    DEPLOYMENTS_LABEL, P2POOL_LABEL, P2POOL_REMOTE_LABEL, P2POOL_SHORT_LABEL,
    PROCEED_LABEL
)
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DEPLOYMENT_MGR_FIELD, DEPLOYMENT_TYPE_FIELD,
    GET_NEW_REC_FIELD, P2POOL_FIELD, REMOTE_FIELD,
    TO_MODULE_FIELD, TO_METHOD_FIELD
)
from db4e.Messages.SubmitFormData import SubmitFormData

STATIC_CONTENT = f"Welcome to the {P2POOL_LABEL} {DEPLOYMENTS_LABEL} screen. "
STATIC_CONTENT += f"On this screen you can choose to deploy a *local* or *remote* "
STATIC_CONTENT += f"{P2POOL_LABEL} {DEPLOYMENTS_LABEL}.\n\nA *local* {P2POOL_LABEL} "
STATIC_CONTENT += f"will run on this machine.\n\n"
STATIC_CONTENT += f"A *remote* {P2POOL_LABEL} {DEPLOYMENTS_LABEL} points at a " 
STATIC_CONTENT += f"{P2POOL_LABEL} that has already been setup. For this type of "
STATIC_CONTENT += f"deployment you will need to know the hostname of the remote system "
STATIC_CONTENT += f"and port numbers that the remote deployment uses."

class NewP2PoolType(Container):

    def compose(self):
        
        with Vertical():
            yield MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro")

            with Vertical(id="new_p2pool_type_form"):
                with RadioSet(id="new_p2pool_type_radioset"):
                    yield RadioButton(P2POOL_LABEL, id="new_p2pool_type_p2pool", value=True)
                    yield RadioButton(P2POOL_REMOTE_LABEL, id="new_p2pool_type_remote_p2pool")

            with Horizontal(id="new_p2pool_type_button"):
                yield Button(label=PROCEED_LABEL, id="new_p2pool_type_proceed_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#new_p2pool_type_radioset", RadioSet)
        selected = radio_set.pressed_button
        if selected.id == "new_p2pool_type_remote_p2pool":
            remote_value = True
        else:
            remote_value = False
        form_data = {
            TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
            TO_METHOD_FIELD: GET_NEW_REC_FIELD,
            COMPONENT_FIELD: P2POOL_FIELD,
            REMOTE_FIELD: remote_value
        }
        self.app.post_message(SubmitFormData(self, form_data))