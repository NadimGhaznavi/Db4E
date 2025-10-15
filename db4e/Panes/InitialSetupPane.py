"""
db4e/Panes/InitialSetupPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.widgets import Label, Input, Button
from textual.containers import Container, Vertical, ScrollableContainer, Horizontal

from db4e.Modules.Db4E import Db4E
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Messages.Quit import Quit

from db4e.Constants.DField import DField
from db4e.Constants.DModule import DModule
from db4e.Constants.DElem import DElem
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DButton import DButton
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm


MAX_GROUP_LENGTH = 20

hi = "cyan"


class InitialSetupPane(Container):

    rec = {}

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.USER, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.USER_NAME_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.GROUP, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.GROUP_NAME_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.INSTALL_DIR, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.INSTALL_DIR_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.USER_WALLET, classes=DForm.FORM_LABEL),
                        Input(
                            restrict=r"[a-zA-Z0-9]*",
                            compact=True,
                            id=DForm.USER_WALLET_INPUT,
                            classes=DForm.INPUT_70,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.VENDOR_DIR, classes=DForm.FORM_LABEL),
                        Input(
                            restrict=r"/[a-zA-Z0-9/_.\- ]*",
                            compact=True,
                            id=DForm.VENDOR_DIR_INPUT,
                            classes=DForm.INPUT_70,
                        ),
                    ),
                    classes=DForm.FORM_5,
                ),
                Vertical(
                    Horizontal(
                        Button(label=DLabel.PROCEED, id=DButton.PROCEED),
                        Button(label=DLabel.ABORT, id=DButton.ABORT),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
                classes=DForm.PANE_BOX,
            ),
            classes=DForm.PANE_BOX,
        )

    def set_data(self, db4e: Db4E):
        # print(f"InitialSetup:set_data(): rec: {rec}")
        self.db4e = db4e
        INTRO = (
            f"Welcome to the [bold {hi}]Database 4 Everything[/] initial "
            f"installation screen. Access to Db4E will be restricted to the [{hi}]user[/] "
            f"and [{hi}]group[/] shown below. Use a [bold]fully qualified path[/] for the "
            f"[{hi}]{DLabel.VENDOR_DIR}[/]."
        )
        self.query_one(f"#{DForm.INTRO}", Label).update(INTRO)
        self.query_one(f"#{DForm.USER_NAME_LABEL}", Label).update(db4e.user())
        self.query_one(f"#{DForm.GROUP_NAME_LABEL}", Label).update(db4e.group())
        self.query_one(f"#{DForm.INSTALL_DIR_LABEL}", Label).update(db4e.install_dir())
        self.query_one(f"#{DForm.USER_WALLET_INPUT}", Input).value = db4e.user_wallet()
        self.query_one(f"#{DForm.VENDOR_DIR_INPUT}", Input).value = db4e.vendor_dir()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        button_id = event.button.id
        if button_id == DButton.PROCEED:
            self.db4e.user_wallet(
                self.query_one(f"#{DForm.USER_WALLET_INPUT}", Input).value
            )
            self.db4e.vendor_dir(
                self.query_one(f"#{DForm.VENDOR_DIR_INPUT}", Input).value
            )
            form_data = {
                DField.TO_MODULE: DModule.INSTALL_MGR,
                DField.TO_METHOD: DMethod.INITIAL_SETUP,
                DField.ELEMENT_TYPE: DElem.DB4E,
                DField.ELEMENT: self.db4e,
            }
            self.app.post_message(RefreshNavPane(self))
            self.app.post_message(Db4eMsg(self, form_data))
        elif button_id == DButton.ABORT:
            self.app.post_message(Quit(self))
