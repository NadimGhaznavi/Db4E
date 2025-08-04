"""
db4e/Panes/Donations.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Label, Input, Button, MarkdownViewer

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.Fields import (
    INFO_MSG_FIELD, PANE_BOX_FIELD)
from db4e.Constants.Labels import (DB4E_LONG_LABEL)
from db4e.Constants.Defaults import (DONATION_WALLET_DEFAULT)

color = "#9cae41"
hi = "#d7e556"

class Donations(Container):

    def compose(self):
        # Local Monero daemon deployment form
        INTRO = f"This screen provides way for you to support the [{hi}]Database " \
            f"4 Everything[/] project."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes="form_intro"),

                Vertical(
                    Label(f"[cyan]{DB4E_LONG_LABEL}[/] project Monero donation wallet:"),
                    Label(f"[{hi}]{DONATION_WALLET_DEFAULT}[/]"), 
                    Label(),
                    Label('Coming Soon: 🚧 [cyan]Paypal[/] 🚧', classes="form_box"),
                    classes=INFO_MSG_FIELD)),
            classes=PANE_BOX_FIELD)
                    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
        # self.app.post_message(Db4eMsg(self, form_data=form_data))