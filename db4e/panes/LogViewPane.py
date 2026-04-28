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

from db4e.messages.Db4EMsg import Db4EMsg

from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DForm import DForm
from db4e.constants.DButton import DButtonF, DButtonL
from db4e.constants.DModule import DModule
from db4e.constants.DMethod import DMethod

NUM_LINES = [
    (DLabel.LINES_100, DField.LINES_100),
    (DLabel.LINES_250, DField.LINES_250),
    (DLabel.LINES_500, DField.LINES_500),
    (DLabel.LINES_1000, DField.LINES_1000),
]


class LogViewPane(Container):

    elem = None

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        yield Vertical(
            RichLog(
                highlight=True, markup=True, id=DForm.LOG_WIDGET, classes=DForm.BOX
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button pressed events.

        :param event: Event payload.
        :type event: Button.Pressed
        :return: None
        :rtype: None
        """
        elem_type = type(self.elem).lower()
        num_lines = self.query_one(f"#{DForm.NUM_LINES}", Select).value
        form_data = {
            DField.TO_MODULE: DModule.NAV_HANDLER,
            DField.TO_METHOD: DMethod.GET_LOG,
            DField.ELEMENT: self.elem,
            DField.ELEMENT_TYPE: elem_type,
            DField.LOG_LINES: num_lines,
        }
        self.app.post_message(Db4EMsg(self, form_data=form_data))

    def set_data(self, elem):
        """Set the data for the pane.

        :param log_lines: Log line list.
        :type log_lines: list
        :return: None
        :rtype: None
        """
        self.elem = elem
        log_lines = elem.log_lines()
        log = self.query_one(f"#{DForm.LOG_WIDGET}", RichLog)
        for line in log_lines:
            log.write(line)
