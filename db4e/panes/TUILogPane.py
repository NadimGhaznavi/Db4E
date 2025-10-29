"""
db4e/Panes/TUILogPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

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

    log_lines = reactive([], always_update=True)
    max_lines = DDef.MAX_LOG_LINES

    def compose(self):
        yield Vertical(
            ScrollableContainer(Static(id=DForm.LOG_WIDGET)), classes=DForm.PANE_BOX
        )

    def set_data(self, log_lines: list):
        # self.log_widget.clear()
        table = Table(
            show_header=True,
            header_style="bold #31b8e6",
            style="#0c323e",
            box=box.SIMPLE,
        )
        table.add_column(DLabel.TIMESTAMP)
        table.add_column(DLabel.STATUS)
        table.add_column(DLabel.OPERATION)
        table.add_column(DLabel.TYPE)
        table.add_column(DLabel.INSTANCE)
        table.add_column(DLabel.MESSAGE)
        table.add_column(DLabel.DETAILS)
        for log_line in log_lines:
            year = log_line.updated_year()
            month = log_line.updated_month()
            day = log_line.updated_day()
            hour = log_line.updated_hour()
            minute = log_line.updated_minute()
            second = log_line.updated_second()

            date = f"{year}-{month:02d}-{day:02d}"
            time = f"{hour:02d}:{minute:02d}:{second:02d}"
            status = log_line.status().upper()
            if status == DStatus.GOOD.upper():
                status = f"[b green]{status}[/]"
            elif status == DStatus.WARN.upper():
                status = f"[b yellow]{status}[/]"
            elif status == DStatus.ERROR.upper():
                status = f"[b red]{status}[/]"
            operation = log_line.operation().capitalize()
            elem = TYPE_TABLE[log_line.tracked_type()]
            instance = log_line.tracked_instance()
            message = log_line.message()
            details = log_line.details() or ""

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
