"""
db4e/Panes/InitialSetup.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from textual.widgets import Label, MarkdownViewer, Input, Button
from textual.containers import Container, Vertical, Horizontal
from textual.app import ComposeResult

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Messages.RefreshNavPane import RefreshNavPane

#from db4e.Messages.SubmitFormData import SubmitFormData

STATIC_CONTENT = """Welcome to the *Database 4 Everything* initial setup screen. 

| Field                | Description                                        | Example          |
| -------------------- | ---------------------------------------------------|----------------- |
| Monero wallet        | Where your mining payments will be sent            | 48aTDJfRH2JLc... |
| Linux group          | A Linux group name                                 | db4e             |
| Deployment directory | A directory for programs, configuration files etc. | /opt/db4e        |

The *Linux group* will be created and the user who is running this program will be added. The 
*deployment directory* will be created and *Monero*, *P2Pool* and *XMRig* will be installed
into this directory.

Additionally, the `/etc/sudoers` will be updated to allow Db4E to start and stop Monero, P2Pool
and XMRig. `Systemd` services will be added for these three elements and a *Db4E* service will also
be installed. Finally, the *sticky bit* will be set on the XMRig executible so it runs as root to
access MSRs for optimal performance.

You must have *sudo* access to the root user account. This is normally already setup in a default 
Linux installation. You will be prompted for your password, since the installer runs as root.
"""

MAX_GROUP_LENGTH = 20

class InitialSetup(Container):

    def compose(self) -> ComposeResult:
        yield Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label("Linux Group:", id="initial_setup_db4e_group_label"),
                    Input(id="initial_setup_db4e_group_input", restrict=r"[a-z0-9]*", max_length=MAX_GROUP_LENGTH, compact=True)),
                Horizontal(
                    Label("Deployment Directory:", id="initial_setup_vendor_dir_label"),
                    Input(id="initial_setup_vendor_dir_input", restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True)),
                Horizontal(
                    Label("Wallet:", id="initial_setup_user_wallet_label"), 
                    Input(id="initial_setup_user_wallet_input", restrict=r"[a-zA-Z0-9]*", compact=True)),
                id="initial_setup_form"),

            Button(label="Proceed", id="initial_setup_button"))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        form_data = {
            "to_module": "InstallMgr",
            "to_method": "initial_setup",
            "user_wallet": self.query_one("#initial_setup_user_wallet_input", Input).value,
            "db4e_group": self.query_one("#initial_setup_db4e_group_input", Input).value,
            "vendor_dir": self.query_one("#initial_setup_vendor_dir_input", Input).value,
        }
        self.app.post_message(SubmitFormData(self, form_data))
        self.app.post_message(RefreshNavPane(self))
