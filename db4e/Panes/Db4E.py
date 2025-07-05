"""
db4e/Panes/Db4E.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from textual.widgets import Label, MarkdownViewer, Input, Button
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult

from db4e.Messages.SubmitFormData import SubmitFormData

STATIC_CONTENT = """Welcome to the *Database 4 Everything Db4E Core* configuration screen.
On this screen uou can update your *Monero wallet* and relocate the *deployment directory*.
"""

class Db4E(Container):

    def set_data(self, db4e_rec):
        print(f"Db4E:set_data(): {db4e_rec}")

        rec_2_biz = {
            'group': 'Db4E Group',
            'install_dir': 'Install Directory',
            'user': 'Db4E User',
            'user_wallet': 'Monero Wallet',
            'vendor_dir': 'Deployment Directory'
        }

        db4e_user_name = rec_2_biz['user']
        db4e_user = db4e_rec['user']
        db4e_group_name = rec_2_biz['group']
        db4e_group = db4e_rec['group']
        install_dir_name = rec_2_biz['install_dir']
        install_dir = db4e_rec['install_dir']
        vendor_dir_name = rec_2_biz['vendor_dir']
        vendor_dir = db4e_rec['vendor_dir']
        user_wallet_name = rec_2_biz['user_wallet']
        user_wallet = db4e_rec['user_wallet']

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

            Button(label="Update", id="db4e_update_button"))
        self.mount(md)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        form_data = {
            "to_module": "DeploymentMgr",
            "to_method": "update_deployment",
            "user_wallet": self.query_one("#initial_setup_user_wallet_input", Input).value,
            "vendor_dir": self.query_one("#initial_setup_vendor_dir_input", Input).value,
        }
        self.app.post_message(SubmitFormData(self, form_data))

