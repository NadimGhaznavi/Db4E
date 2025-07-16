"""
db4e/Panes/InitialSetup.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from textual.widgets import Label, MarkdownViewer, Input, Button, Static
from textual.containers import Container, Vertical, Horizontal

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Messages.Quit import Quit

from db4e.Constants.Fields import (
    COMPONENT_FIELD, DB4E_FIELD, FORM_DATA_FIELD, GROUP_FIELD, INITIAL_SETUP_FIELD, 
    INSTALL_MGR_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, VENDOR_DIR_FIELD, USER_FIELD,
    USER_WALLET_FIELD
)
from db4e.Constants.Labels import (
    ABORT_LABEL, GROUP_LABEL, DEPLOYMENT_DIR_LABEL, MONERO_WALLET_LABEL, 
    PROCEED_LABEL, USER_LABEL
)

STATIC_CONTENT = """Welcome to the *Database 4 Everything* initial setup screen. 

This setup will configure your deployment using your current Linux user and group. 
It is recommended that you use a dedicated Linux user and group.

1. Press the **Abort** button below to exit this setup.
2. From your shell, create the required user and group (e.g., `db4e`).
3. Restart the Db4E application after creating the appropriate user and group.

The installer will:

* Create a *deployment directory* to house the *Db4E*, *Monero*, *P2Pool* 
and *XMRig* software, settings, log files etc. 
* Create a **/etc/sudoers.d/db4e** file to allow Db4E to start and stop Db4E, Monero 
daemon, P2Pool and XMRig. 
* Create *systemd* services will be added for the above four elements. 
* Set the *SETUID* bit on the XMRig executible so it runs as root to access MSRs 
for optimal performance.

You must have passwordless *sudo* access to the root user account. You may need to
modify the */etc/sudoers*:

```
TYPICAL DEFAULT    :   %sudo	ALL=(ALL:ALL) ALL
INSTALLER REQUIRES :   %sudo	ALL=(ALL:ALL) NOPASSWD: ALL
```

Once you have completed this step you can restore the */etc/sudoers* file.
"""

MAX_GROUP_LENGTH = 20

class InitialSetup(Container):

    user_name_static = Static("", id="user_name_input")
    group_name_static = Static("", id="group_name_input")
    vendor_dir_input = Input(restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True, id="vendor_dir_input")
    user_wallet_input = Input(restrict=r"[a-zA-Z0-9]*", compact=True, id="user_wallet_input")

    def compose(self):
        yield Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(USER_LABEL, id="user_name_label"),
                    self.user_name_static),
                Horizontal(
                    Label(GROUP_LABEL, id="group_name_label"),
                    self.group_name_static),
                Horizontal(
                    Label(DEPLOYMENT_DIR_LABEL, id="vendor_dir_label"),
                    self.vendor_dir_input),
                Horizontal(
                    Label(MONERO_WALLET_LABEL, id="user_wallet_label"), 
                    self.user_wallet_input),
                id="initial_setup_form"),

            Horizontal(
                Button(label=PROCEED_LABEL, id="proceed_button"),
                Button(label=ABORT_LABEL, id="abort_button"),
                id="buttons"))

    def set_data(self, account_info: dict):
        self.user_name_static.update(account_info[USER_FIELD])
        self.group_name_static.update(account_info[GROUP_FIELD])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        button_id = event.button.id
        if button_id == "proceed_button":        
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
        else:
            self.app.post_message(Quit(self))
