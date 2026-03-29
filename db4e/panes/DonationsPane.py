# db4e/Panes/DonationsPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Label, Button

from db4e.constants.DLabel import DLabel
from db4e.constants.DDef import DDef
from db4e.constants.DForm import DForm

color = "#9cae41"
hi = "#d7e556"


class DonationsPane(Container):
    """Textual pane for DonationsPane."""

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        # Local Monero daemon deployment form
        INTRO = (
            f"This screen provides way for you to support the [{hi}]Database "
            f"4 Everything[/] project."
        )

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes="form_intro"),
                Vertical(
                    Label(f"[cyan]{DLabel.DB4E_LONG}[/] Monero wallet:"),
                    Label(f"[{hi}]{DDef.DONATION_WALLET}[/]"),
                    Label(),
                    Label(f"[cyan]PayPal[/] account:"),
                    Label(f"[{hi}]{DDef.PAYPAL_DONATIONS}"),
                    Label(),
                    Label(f"eTransfer:"),
                    Label(f"[{hi}]{DDef.EMAIL}"),
                    classes=DForm.INFO_MSG,
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button pressed events.

        :param event: Event payload.
        :type event: Button.Pressed
        :return: None
        :rtype: None
        """
        pass
        # self.app.post_message(Db4EMsg(self, form_data=form_data))
