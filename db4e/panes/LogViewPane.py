# db4e/Panes/Db4EPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from rich.text import Text

from textual.reactive import reactive
from textual.widgets import RichLog
from textual.containers import (
    Container,
    Vertical,
)

from db4e.constants.DForm import DForm


class LogViewPane(Container):

    log_lines = reactive([], always_update=True)

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        yield Vertical(
            RichLog(highlight=False, markup=True, id=DForm.LOG_WIDGET),
            classes=DForm.PANE_BOX,
        )
