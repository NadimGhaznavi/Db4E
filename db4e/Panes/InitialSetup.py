"""
db4e/Panes/InitialSetup.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from textual.widgets import Label, Input, Button
from textual.containers import Container, Vertical, ScrollableContainer, Horizontal

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Messages.Quit import Quit

from db4e.Constants.Fields import (
    ABORT_BUTTON_FIELD, COMPONENT_FIELD, DB4E_FIELD, FORM_4_FIELD, FORM_DATA_FIELD, 
    FORM_INPUT_30_FIELD, FORM_INTRO_FIELD, FORM_INPUT_70_FIELD, FORM_LABEL_FIELD, 
    GREEN_BUTTON_FIELD, GROUP_FIELD, INITIAL_SETUP_FIELD, INSTALL_MGR_FIELD, 
    PROCEED_BUTTON_FIELD, RED_BUTTON_FIELD, STATIC_CONTENT_FIELD, TO_METHOD_FIELD, 
    TO_MODULE_FIELD, VENDOR_DIR_FIELD, USER_FIELD, USER_WALLET_FIELD)
from db4e.Constants.Labels import (
    ABORT_LABEL, GROUP_LABEL, DEPLOYMENT_DIR_LABEL, MONERO_WALLET_LABEL, 
    PROCEED_LABEL, USER_LABEL)

MAX_GROUP_LENGTH = 20

class InitialSetup(Container):

    user_name_static = Label("", classes=STATIC_CONTENT_FIELD)
    group_name_static = Label("", classes=STATIC_CONTENT_FIELD)
    vendor_dir_input = Input(
        restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True, id="vendor_dir_input", 
        classes=FORM_INPUT_30_FIELD)
    user_wallet_input = Input(
        restrict=r"[a-zA-Z0-9]*", compact=True, id="user_wallet_input", 
        classes=FORM_INPUT_70_FIELD)

    def compose(self):
        INTRO = "Welcome to the [bold cyan]Database 4 Everything[/] initial " \
        f"installation screen. Access to Db4E will be restricted to the [cyan]user[/] " \
        f"and [cyan]group[/] shown below."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Horizontal(
                        Label(USER_LABEL, classes=FORM_LABEL_FIELD),
                        self.user_name_static),
                    Horizontal(
                        Label(GROUP_LABEL, classes=FORM_LABEL_FIELD),
                        self.group_name_static),
                    Horizontal(
                        Label(DEPLOYMENT_DIR_LABEL, classes=FORM_LABEL_FIELD),
                        self.vendor_dir_input),
                    Horizontal(
                        Label(MONERO_WALLET_LABEL,classes=FORM_LABEL_FIELD), 
                        self.user_wallet_input),
                    classes=FORM_4_FIELD),

                Vertical(
                    Horizontal(
                        Button(label=PROCEED_LABEL, id=PROCEED_BUTTON_FIELD, 
                            classes=GREEN_BUTTON_FIELD),
                        Button(label=ABORT_LABEL, id=ABORT_BUTTON_FIELD, classes=RED_BUTTON_FIELD),
                        classes="button_row")),

                classes="pane_box"))

    def set_data(self, account_info: dict):
        self.user_name_static.update(account_info[USER_FIELD])
        self.group_name_static.update(account_info[GROUP_FIELD])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        button_id = event.button.id
        if button_id == PROCEED_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: INSTALL_MGR_FIELD,
                TO_METHOD_FIELD: INITIAL_SETUP_FIELD,
                COMPONENT_FIELD: DB4E_FIELD,
                FORM_DATA_FIELD: True,
                USER_WALLET_FIELD: self.query_one("#user_wallet_input", Input).value,
                VENDOR_DIR_FIELD: self.query_one("#vendor_dir_input", Input).value,
            }
            self.app.post_message(RefreshNavPane(self))
            self.app.post_message(SubmitFormData(self, form_data))
        elif button_id == ABORT_BUTTON_FIELD:
            self.app.post_message(Quit(self))
