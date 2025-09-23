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
    user_name_static = Label("", classes=DForm.STATIC)
    group_name_static = Label("", classes=DForm.STATIC)
    install_dir_static = Label("", classes=DForm.STATIC)
    vendor_dir_input = Input(
        restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True, id=DForm.VENDOR_DIR_INPUT, 
        classes=DForm.INPUT_70)
    user_wallet_input = Input(
        restrict=r"[a-zA-Z0-9]*", compact=True, id=DForm.USER_WALLET_INPUT, 
        classes=DForm.INPUT_70)

    def compose(self):
        INTRO = f"Welcome to the [bold {hi}]Database 4 Everything[/] initial " \
        f"installation screen. Access to Db4E will be restricted to the [{hi}]user[/] " \
        f"and [{hi}]group[/] shown below. Use a [bold]fully qualified path[/] for the " \
        f"[{hi}]{DLabel.VENDOR_DIR}[/]."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.USER, classes=DForm.FORM_LABEL),
                        self.user_name_static),
                    Horizontal(
                        Label(DLabel.GROUP, classes=DForm.FORM_LABEL),
                        self.group_name_static),
                    Horizontal(
                        Label(DLabel.INSTALL_DIR, classes=DForm.FORM_LABEL),
                        self.install_dir_static),
                    Horizontal(
                        Label(DLabel.USER_WALLET,classes=DForm.FORM_LABEL), 
                        self.user_wallet_input),
                    Horizontal(
                        Label(DLabel.VENDOR_DIR, classes=DForm.FORM_LABEL),
                        self.vendor_dir_input),
                    classes=DForm.FORM_5),

                Vertical(
                    Horizontal(
                        Button(label=DLabel.PROCEED, id=DButton.PROCEED),
                        Button(label=DLabel.ABORT, id=DButton.ABORT),
                        classes=DForm.BUTTON_ROW)),
                classes=DForm.PANE_BOX),

            classes=DForm.PANE_BOX)


    def set_data(self, db4e: Db4E):
        #print(f"InitialSetup:set_data(): rec: {rec}")
        self.db4e = db4e
        self.user_name_static.update(db4e.user())
        self.group_name_static.update(db4e.group())
        self.install_dir_static.update(db4e.install_dir())
        self.user_wallet_input.value = db4e.user_wallet()
        self.vendor_dir_input.value = db4e.vendor_dir()


    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        button_id = event.button.id
        if button_id == DButton.PROCEED:
            self.db4e.user_wallet(self.query_one("#" + DForm.USER_WALLET_INPUT, Input).value)
            self.db4e.vendor_dir(self.query_one("#" + DForm.VENDOR_DIR_INPUT, Input).value)
            form_data = {
                DField.TO_MODULE: DModule.INSTALL_MGR,
                DField.TO_METHOD: DMethod.INITIAL_SETUP,
                DField.ELEMENT_TYPE: DElem.DB4E,
                DField.ELEMENT: self.db4e
            }
            self.app.post_message(RefreshNavPane(self))
            self.app.post_message(Db4eMsg(self, form_data))
        elif button_id == DButton.ABORT:
            self.app.post_message(Quit(self))
