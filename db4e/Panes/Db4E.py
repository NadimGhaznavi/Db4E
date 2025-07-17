"""
db4e/Panes/Db4E.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual import on
from textual.widgets import Label, MarkdownViewer, Input, Button, Static
from textual.containers import Container, Vertical, Horizontal
from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DB4E_FIELD, DEPLOYMENT_MGR_FIELD, FORM_DATA_FIELD, GROUP_FIELD, 
    INSTALL_DIR_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, UPDATE_DEPLOYMENT_FIELD, 
    USER_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD)
from db4e.Constants.Labels import (
    DB4E_GROUP_LABEL, DB4E_USER_LABEL, DEPLOYMENT_DIR_LABEL, INSTALL_DIR_LABEL, 
    MONERO_WALLET_LABEL, UPDATE_LABEL)


class Db4E(Container):

    user_name_label = Label("", classes="static_content")
    group_name_label = Label("", classes="static_content")
    install_dir_label = Label("", classes="static_content")
    vendor_dir_input = Input(restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True, id="vendor_dir_input", classes="form_input")
    user_wallet_input = Input(restrict=r"[a-zA-Z0-9]*", compact=True, id="user_wallet_input", classes="form_input")

    def compose(self):
        INTRO = "Welcome to the [bold green]Database 4 Everything Core[/] [green bold]configuration "
        INTRO += "screen[/]. On this screen you can update your [cyan]Monero Wallet[/] and "
        INTRO += "relocate the [cyan]Deployment Directory[/]. "
        yield Vertical(
            Label(INTRO, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(DB4E_USER_LABEL, classes="form_label"),
                    self.user_name_label),
                Horizontal(
                    Label(DB4E_GROUP_LABEL, classes="form_label"),
                    self.group_name_label),
                Horizontal(
                    Label(INSTALL_DIR_LABEL, classes="form_label"),
                    self.install_dir_label),
                Horizontal(
                    Label(DEPLOYMENT_DIR_LABEL, classes="form_label"),
                    self.vendor_dir_input),
                Horizontal(
                    Label(MONERO_WALLET_LABEL, classes="form_label"),
                    self.user_wallet_input),
                id="db4e_update_form"),

            Button(label=UPDATE_LABEL, classes="update_button"))

    def set_data(self, db4e_rec):
        #print(f"Db4E:set_data(): {db4e_rec}")

        self.user_name_label.update(db4e_rec[USER_FIELD] or "")
        self.group_name_label.update(db4e_rec[GROUP_FIELD] or "")
        self.install_dir_label.update(db4e_rec[INSTALL_DIR_FIELD] or "" )
        self.vendor_dir_input.value = db4e_rec[VENDOR_DIR_FIELD] or ""
        self.user_wallet_input.value = db4e_rec[USER_WALLET_FIELD] or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        form_data = {
            TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
            TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
            COMPONENT_FIELD: DB4E_FIELD,
            FORM_DATA_FIELD: True,
            USER_WALLET_FIELD: self.query_one("#user_wallet_input", Input).value,
            VENDOR_DIR_FIELD: self.query_one("#vendor_dir_input", Input).value,
        }
        self.app.post_message(SubmitFormData(self, form_data=form_data))

