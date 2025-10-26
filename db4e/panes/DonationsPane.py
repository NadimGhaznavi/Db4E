"""
db4e/Panes/DonationsPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Label, Button

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DDef import DDef
from db4e.Constants.DForm import DForm

color = "#9cae41"
hi = "#d7e556"

class DonationsPane(Container):

    def compose(self):
        # Local Monero daemon deployment form
        INTRO = f"This screen provides way for you to support the [{hi}]Database " \
            f"4 Everything[/] project."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes="form_intro"),

                Vertical(
                    Label(f"[cyan]{DLabel.DB4E_LONG}[/] project Monero donation wallet:"),
                    Label(f"[{hi}]{DDef.DONATION_WALLET}[/]"), 
                    Label(),
                    Label('Coming Soon: 🚧 [cyan]Paypal[/] 🚧', classes=DForm.PANE_BOX),
                    classes=DForm.INFO_MSG)),
            classes=DForm.PANE_BOX)
                    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
        # self.app.post_message(Db4eMsg(self, form_data=form_data))