"""
db4e/Panes/InitialSetupPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.widgets import Label, Input, Button, Static
from textual.containers import Container, Vertical, ScrollableContainer, Horizontal

from db4e.Modules.Db4E import Db4E
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Messages.Quit import Quit

from db4e.Constants.Fields import (
    ELEMENT_TYPE_FIELD, DB4E_FIELD, FORM_5_FIELD, 
    ELEMENT_FIELD, FORM_INTRO_FIELD, FORM_INPUT_70_FIELD, FORM_LABEL_FIELD, 
    INITIAL_SETUP_FIELD, INSTALL_MGR_FIELD, 
    STATIC_CONTENT_FIELD, TO_METHOD_FIELD, 
    TO_MODULE_FIELD)
from db4e.Constants.Labels import (
    GROUP_LABEL, VENDOR_DIR_LABEL, USER_WALLET_LABEL, INSTALL_DIR_LABEL,
    USER_LABEL)
from db4e.Constants.Buttons import (
    ABORT_BUTTON_FIELD, ABORT_LABEL, PROCEED_BUTTON_FIELD, PROCEED_LABEL, 
)

MAX_GROUP_LENGTH = 20

hi = "cyan"

class InitialSetupPane(Container):

    rec = {}
    user_name_static = Label("", classes=STATIC_CONTENT_FIELD)
    group_name_static = Label("", classes=STATIC_CONTENT_FIELD)
    install_dir_static = Label("", classes=STATIC_CONTENT_FIELD)
    vendor_dir_input = Input(
        restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True, id="vendor_dir_input", 
        classes=FORM_INPUT_70_FIELD)
    user_wallet_input = Input(
        restrict=r"[a-zA-Z0-9]*", compact=True, id="user_wallet_input", 
        classes=FORM_INPUT_70_FIELD)

    def compose(self):
        INTRO = f"Welcome to the [bold {hi}]Database 4 Everything[/] initial " \
        f"installation screen. Access to Db4E will be restricted to the [{hi}]user[/] " \
        f"and [{hi}]group[/] shown below. Use a [bold]fully qualified path[/] for the " \
        f"[{hi}]{VENDOR_DIR_LABEL}[/]."

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
                        Label(INSTALL_DIR_LABEL, classes=FORM_LABEL_FIELD),
                        self.install_dir_static),
                    Horizontal(
                        Label(USER_WALLET_LABEL,classes=FORM_LABEL_FIELD), 
                        self.user_wallet_input),
                    Horizontal(
                        Label(VENDOR_DIR_LABEL, classes=FORM_LABEL_FIELD),
                        self.vendor_dir_input),
                    classes=FORM_5_FIELD),

                Vertical(
                    Horizontal(
                        Button(label=PROCEED_LABEL, id=PROCEED_BUTTON_FIELD),
                        Button(label=ABORT_LABEL, id=ABORT_BUTTON_FIELD),
                        classes="button_row")),
                classes="page_box"),

            classes="pane_box")


    def set_data(self, db4e: Db4E):
        #print(f"InitialSetup:set_data(): rec: {rec}")
        self.db4e = db4e
        self.user_name_static.update(db4e.user.value)
        self.group_name_static.update(db4e.group.value)
        self.install_dir_static.update(db4e.install_dir.value)
        self.user_wallet_input.value = db4e.user_wallet.value
        self.vendor_dir_input.value = db4e.vendor_dir.value


    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        button_id = event.button.id
        if button_id == PROCEED_BUTTON_FIELD:
            self.db4e.user_wallet.value = self.query_one("#user_wallet_input", Input).value
            self.db4e.vendor_dir.value = self.query_one("#vendor_dir_input", Input).value
            form_data = {
                TO_MODULE_FIELD: INSTALL_MGR_FIELD,
                TO_METHOD_FIELD: INITIAL_SETUP_FIELD,
                ELEMENT_TYPE_FIELD: DB4E_FIELD,
                ELEMENT_FIELD: self.db4e
            }
            self.app.post_message(RefreshNavPane(self))
            self.app.post_message(Db4eMsg(self, form_data))
        elif button_id == ABORT_BUTTON_FIELD:
            self.app.post_message(Quit(self))
