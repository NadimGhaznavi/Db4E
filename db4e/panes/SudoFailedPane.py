# db4e/Panes/SudoFailedPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

import getpass

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Label, Button

from db4e.messages.Quit import Quit
from db4e.constants.DForm import DForm
from db4e.constants.DLabel import DLabel

hi = "#64e631"
code = "#bbbbbb"


class SudoFailedPane(Container):
    """Textual pane for a failed sudo configuration"""

    def compose(self) -> ComposeResult:
        username = getpass.getuser()

        yield Vertical(
            Label(f"[b {hi}]FATAL ERROR[/]"),
            Label(""),
            Label("The [b]Db4E Installer[/] requires passwordless sudo access."),
            Label(""),
            Label("Add a line like this to the /etc/suoders file:"),
            Label(""),
            Label(f"[{code}]     {username} ALL=(ALL:ALL) NOPASSWD: ALL[/]"),
            Label(""),
            Label("Use visudo to edit the sudoers configuration safely."),
            Label("After installation, you can remove this entry."),
            Label(""),
            Button(DLabel.EXIT),
            classes=DForm.PANE_BOX,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.post_message(Quit(self))
