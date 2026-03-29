# db4e/Panes/TUILogPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from rich import box
from rich.table import Table

from textual.reactive import reactive
from textual.widgets import Static
from textual.containers import ScrollableContainer, Vertical

from db4e.constants.DElem import DElem
from db4e.constants.DLabel import DLabel
from db4e.constants.DForm import DForm
from db4e.constants.DDef import DDef
from db4e.constants.DSQL import DCol
from db4e.constants.DStatus import DStatus
from db4e.constants.DField import DField

from db4e.recs.ops.TUILogLine import TUILogLine


TYPE_TABLE = {
    DElem.DB4E: DLabel.DB4E,
    DElem.MONEROD: DLabel.MONEROD_SHORT,
    DElem.MONEROD_REMOTE: DLabel.MONEROD_REMOTE_SHORT,
    DElem.P2POOL: DLabel.P2POOL_SHORT,
    DElem.P2POOL_INTERNAL: DLabel.P2POOL_INTERNAL_SHORT,
    DElem.P2POOL_REMOTE: DLabel.P2POOL_REMOTE_SHORT,
    DElem.XMRIG: DLabel.XMRIG_SHORT,
}


class TUILogPane(Static):
    """Textual pane for TUILogPane."""

    log_lines = reactive([], always_update=True)
    max_lines = DDef.MAX_LOG_LINES

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        yield Vertical(
            ScrollableContainer(Static(id=DForm.LOG_WIDGET)), classes=DForm.PANE_BOX
        )

    def set_data(self, log_lines: list):
        """Set the data for the pane.

        :param log_lines: Log line list.
        :type log_lines: list
        :return: None
        :rtype: None
        """
        # self.log_widget.clear()
        table = Table(
            show_header=True,
            header_style="bold #31b8e6",
            style="#0c323e",
            box=box.SIMPLE,
        )
        # print(log_lines)
        table.add_column(DLabel.TIMESTAMP)
        table.add_column(DLabel.STATUS)
        table.add_column(DLabel.OPERATION)
        table.add_column(DLabel.TYPE)
        table.add_column(DLabel.INSTANCE)
        table.add_column(DLabel.MESSAGE)
        table.add_column(DLabel.DETAILS)
        for log_line in log_lines:

            # Handle dict log_line messages
            if isinstance(log_line, dict):
                year = log_line[DField.UPDATED_Y]
                month = log_line[DField.UPDATED_MO]
                day = log_line[DField.UPDATED_D]
                hour = log_line[DField.UPDATED_H]
                minute = log_line[DField.UPDATED_MI]
                second = log_line[DField.UPDATED_S]
                status = log_line[DField.STATUS].upper()
                operation = log_line[DField.OPERATION].capitalize()
                tracked_type = log_line.get(DCol.TRACKED_TYPE, "")
                instance = log_line.get(DCol.TRACKED_INSTANCE) or ""
                message = log_line.get(DField.MESSAGE) or ""
                details = log_line.get(DField.DETAILS) or ""

            # Handle TUILogLine messages
            elif isinstance(log_line, TUILogLine):
                year = log_line.updated_year()
                month = log_line.updated_month()
                day = log_line.updated_day()
                hour = log_line.updated_hour()
                minute = log_line.updated_minute()
                second = log_line.updated_second()
                status = log_line.status().upper()
                operation = log_line.operation()
                tracked_type = log_line.tracked_type() or ""
                instance = log_line.tracked_instance() or ""
                message = log_line.message() or ""
                details = log_line.details() or ""

            date = f"{year}-{month:02d}-{day:02d}"
            time = f"{hour:02d}:{minute:02d}:{second:02d}"
            if status == DStatus.GOOD.upper():
                status = f"[b green]{status}[/]"
            elif status == DStatus.WARN.upper():
                status = f"[b yellow]{status}[/]"
            elif status == DStatus.ERROR.upper():
                status = f"[b red]{status}[/]"

            if tracked_type:
                elem = TYPE_TABLE[tracked_type]
            else:
                elem = ""

            table.add_row(
                f"[b]{date}[/] [b green]{time}[/]",
                status,
                f"[b]{operation}[/]",
                elem,
                f"[yellow]{instance}[/]",
                message,
                f"[b]{details}[/]",
            )

        self.query_one(f"#{DForm.LOG_WIDGET}", Static).update(table)
