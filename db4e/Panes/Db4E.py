"""
db4e/Panes/Db4E.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from textual import on
from textual.widgets import Label, MarkdownViewer, Input, Button
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult
from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DB4E_FIELD, DEPLOYMENT_MGR_FIELD, FORM_DATA_FIELD, GROUP_FIELD, 
    INSTALL_DIR_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, UPDATE_DEPLOYMENT_FIELD, 
    USER_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD
)
from db4e.Constants.Labels import (
    DB4E_GROUP_LABEL, DB4E_USER_LABEL, DEPLOYMENT_DIR_LABEL, INSTALL_DIR_LABEL, MONERO_WALLET_LABEL, PROCEED_LABEL, UPDATE_LABEL
)

STATIC_CONTENT = """Welcome to the *Database 4 Everything Db4E Core* configuration screen.
On this screen uou can update your *Monero wallet* and relocate the *deployment directory*.
"""

class Db4E(Container):

    def set_data(self, db4e_rec):
        print(f"Db4E:set_data(): {db4e_rec}")

        # Record name to human readible name mapping
        rec_2_biz = {
            GROUP_FIELD: DB4E_GROUP_LABEL,
            INSTALL_DIR_FIELD: INSTALL_DIR_LABEL,
            USER_FIELD: DB4E_USER_LABEL,
            USER_WALLET_FIELD: MONERO_WALLET_LABEL,
            VENDOR_DIR_FIELD: DEPLOYMENT_DIR_LABEL
        }

        db4e_user_name = rec_2_biz[USER_FIELD]
        db4e_user = db4e_rec[USER_FIELD] or ""
        db4e_group_name = rec_2_biz[GROUP_FIELD]
        db4e_group = db4e_rec[GROUP_FIELD] or ""
        install_dir_name = rec_2_biz[INSTALL_DIR_FIELD]
        install_dir = db4e_rec[INSTALL_DIR_FIELD] or "" 
        vendor_dir_name = rec_2_biz[VENDOR_DIR_FIELD]
        vendor_dir = db4e_rec[VENDOR_DIR_FIELD] or ""
        user_wallet_name = rec_2_biz[USER_WALLET_FIELD]
        user_wallet = db4e_rec[USER_WALLET_FIELD] or ""

        md = Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(db4e_user_name, id="db4e_user_name_label"),
                    Label(db4e_user, id="db4e_user")),
                Horizontal(
                    Label(db4e_group_name, id="db4e_group_name_label"),
                    Label(db4e_group, id="db4e_group")),
                Horizontal(
                    Label(install_dir_name, id="db4e_install_dir_name_label"),
                    Label(install_dir, id="install_dir")),
                Horizontal(
                    Label(vendor_dir_name, id="db4e_vendor_dir_name_label"),
                    Input(restrict=r"/[a-zA-Z0-9/_.\- ]*", value=vendor_dir, compact=True, id="db4e_vendor_dir_input")),
                Horizontal(
                    Label(user_wallet_name, id="db4e_user_wallet_name_label"),
                    Input(restrict=r"[a-zA-Z0-9]*", value=user_wallet, compact=True, id="db4e_user_wallet_input")),
                id="db4e_update_form"),

            Button(label=UPDATE_LABEL, id="db4e_update_button"))
        self.remove_children()
        self.mount(md)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        print("Db4E:on_button_pressed(): NEVER GETS PRINTED!!!")
        form_data = {
            TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
            TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
            COMPONENT_FIELD: DB4E_FIELD,
            FORM_DATA_FIELD: True,
            USER_WALLET_FIELD: self.query_one("#db4e_user_wallet_input", Input).value,
            VENDOR_DIR_FIELD: self.query_one("#db4e_vendor_dir_input", Input).value,
        }
        print(f"Db4E:on_button_pressed() {form_data}")
        self.app.post_message(SubmitFormData(self, form_data=form_data))

