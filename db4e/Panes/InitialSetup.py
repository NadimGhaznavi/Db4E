"""
db4e/Panes/InitialSetup.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from textual.widgets import Label, MarkdownViewer
from textual.containers import Container
from textual.app import ComposeResult
from textual.message import Message


STATIC_CONTENT = """\
# Initial Setup

Welcome to the *Database 4 Everything* initial setup screen. 
In order to continue, you will need to enter the following information:

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
be installed. Finally, the *sticky bit* will be set on the XMRig executible so it runs as root so
that it can access MSRs for performance purposes.

You must have *sudo* access to the root user account. This is normally already setup in a default 
Linux installation. You will be prompted for your password, since the installer runs as root.
"""

from textual.containers import Vertical
from db4e.Widgets.LabeledInput import LabeledInput
from db4e.Widgets.LabeledButton import LabeledButton

class InitialSetup(Container):

    class UpdateTopBar(Message):
        def __init__(self, component: str, msg: str) -> None:
            super().__init__()
            self.component = component
            self.msg = msg

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="markdown")

    async def on_mount(self):
        print('Welcome:on_mount()')
        self.post_message(self.UpdateTopBar(component="Database 4 Everything", msg="Initial Setup"))

        yield Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="markdown"),
            LabeledInput(label="Monero wallet", placeholder="48aTDJfRH2JLc...", id="user_wallet_input"),
            LabeledInput(label="Linux group", placeholder="db4e", id="db4e_group_input"),
            LabeledInput(label="Deployment directory", placeholder="/opt/db4e", id="vendor_dir_input"),
            LabeledButton(label="Proceed", id="proceed_button"),
        )

    async def on_labeled_input_changed(self, message: LabeledInput.Changed):
        print(f"Input {message.sender.id} changed to: {message.value}")

    async def on_themed_button_pressed(self, message: LabeledButton.Pressed):
        print(f"Button {message.sender.id} pressed!")
        # proceed with validation, etc.
