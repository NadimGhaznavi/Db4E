# db4e/Panes/TUILogPane.py
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
    DElem.P2POOL_INTERNAL: DLabel.P2POOL_INT,
    DElem.P2POOL_REMOTE: DLabel.P2POOL_REMOTE_SHORT,
    DElem.XMRIG: DLabel.XMRIG_SHORT,
}


class TUILogPane(Container):
    """Textual pane for TUILogPane."""

    log_lines = reactive([], always_update=True)
    max_lines = DDef.MAX_LOG_LINES

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        yield Vertical(
            RichLog(highlight=False, markup=True, id=DForm.LOG_WIDGET),
            classes=DForm.PANE_BOX,
        )

    def set_data(self, log_lines: list):
        """Set the data for the pane.

        :param log_lines: Log line list.
        :type log_lines: list
        :return: None
        :rtype: None
        """
        # self.log_widget.clear()
        log_widget = self.query_one(f"#{DForm.LOG_WIDGET}", RichLog)
        log_widget.clear()

        log_widget.write(
            f"[b cyan]{DLabel.DATE:<10s}  {DLabel.TIME:<8s}[/]  "
            f"[b cyan]{DLabel.STATUS:<10s}[/]  "
            f"[b cyan]{DLabel.OP:<7s}[/]  "
            f"[b cyan]{DLabel.TYPE:<13s}[/]  "
            f"[b cyan]{DLabel.INSTANCE:<18s}[/]  "
            f"[b cyan]{DLabel.MESSAGE:<20s}[/]  "
            f"[b cyan]{DLabel.DETAILS:<20s}[/]  "
        )
        log_widget.write(
            f"[b cyan]━━━━━━━━━━  ━━━━━━━━  [/]"
            f"[b cyan]━━━━━━━━━━  [/]"
            f"[b cyan]━━━━━━━  [/]"
            f"[b cyan]━━━━━━━━━━━━━  [/]"
            f"[b cyan]━━━━━━━━━━━━━━━━━━  [/]"
            f"[b cyan]━━━━━━━━━━━━━━━━━━━━  [/]"
            f"[b cyan]━━━━━━━━━━━━━━━━━━━━  [/]"
        )
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
                operation = log_line.operation().capitalize()
                tracked_type = log_line.tracked_type() or ""
                instance = log_line.tracked_instance() or ""
                message = log_line.message() or ""
                details = log_line.details() or ""

            date_str = f"{year}-{month:02d}-{day:02d}"
            date_text = Text(f"{date_str:<10}", style="green")

            time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
            time_text = Text(f"{time_str:<8}")
            operation = Text(f"{operation:<7}", style="yellow")
            instance = Text(f"{instance:<18}", style="bold light_salmon3")
            message = Text(f"{message:<20}", style="bold")
            details = Text(f"{details:<20}")

            if status == DStatus.GOOD.upper() or status == DStatus.COMPLETE.upper():
                status_text = Text(f"{status:>10}", style="bold green")
            elif status == DStatus.WARN.upper():
                status_text = Text(f"{status:>10}", style="bold yellow")
            elif status == DStatus.ERROR.upper():
                status_text = Text(f"{status:>10}", style="bold red")
            else:
                raise ValueError(f"Unrecognized status: {status}")

            if tracked_type:
                elem = TYPE_TABLE[tracked_type]
            else:
                elem = ""
            elem = Text(f"{elem:<13}", style="light_salmon3")

            row = Text()
            row.append_text(date_text)
            row.append("  ")
            row.append_text(time_text)
            row.append("  ")
            row.append_text(status_text)
            row.append("  ")
            row.append_text(operation)
            row.append("  ")
            row.append_text(elem)
            row.append("  ")
            row.append_text(instance)
            row.append("  ")
            row.append_text(message)
            row.append("  ")
            row.append_text(details)

            log_widget.write(row)
