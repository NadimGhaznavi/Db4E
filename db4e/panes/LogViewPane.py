# db4e/Panes/Db4EPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0

from rich.text import Text

from textual.reactive import reactive
from textual.widgets import RichLog, Button, Select
from textual.containers import (
    Container,
    Vertical,
    Horizontal,
)

from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DForm import DForm
from db4e.constants.DButton import DButtonF, DButtonL

NUM_LINES = [
    (DLabel.LINES_100, DField.LINES_100),
    (DLabel.LINES_250, DField.LINES_250),
    (DLabel.LINES_500, DField.LINES_500),
    (DLabel.LINES_1000, DField.LINES_1000),
]


class LogViewPane(Container):

    log_lines = reactive([], always_update=True)

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        yield Vertical(
            RichLog(
                highlight=False, markup=True, id=DForm.LOG_WIDGET, classes=DForm.BOX
            ),
            Horizontal(
                Select(
                    NUM_LINES,
                    compact=True,
                    id=DForm.NUM_LINES,
                    allow_blank=False,
                    classes=DForm.BOX,
                ),
                Button(label=DButtonL.REFRESH, id=DButtonF.REFRESH),
                classes=DForm.BUTTON_ROW,
            ),
            classes=DForm.PANE_BOX,
        )
