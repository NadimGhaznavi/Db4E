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

from db4e.Constants.DElem import DElem
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm
from db4e.Constants.DDef import DDef
from db4e.Constants.DField import DField



TYPE_TABLE = {
    DElem.DB4E: DLabel.DB4E,
    DElem.INT_P2POOL: DLabel.P2POOL_INTERNAL_SHORT,
    DElem.MONEROD: DLabel.MONEROD_SHORT,
    DElem.MONEROD_REMOTE: DLabel.MONEROD_REMOTE_SHORT,
    DElem.P2POOL: DLabel.P2POOL_SHORT,
    DElem.P2POOL_REMOTE: DLabel.P2POOL_REMOTE_SHORT,
    DElem.XMRIG: DLabel.XMRIG_SHORT,
}

class TUILogPane(Static):

    log_lines = reactive([], always_update=True)
    max_lines = DDef.MAX_LOG_LINES
    #log_widget = Log(highlight=True, auto_scroll=True, classes=PANE_BOX_FIELD)
    #log_widget = RichLog(highlight=True, auto_scroll=True, classes=PANE_BOX_FIELD)
    log_widget = Static()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.results = Static()

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                self.log_widget
            ),
            classes=DForm.PANE_BOX)

    def set_data(self, jobs_list: list):
        #self.log_widget.clear()
        table = Table(show_header=True, header_style="bold #31b8e6", style="#0c323e", box=box.SIMPLE)
        table.add_column(DLabel.TIMESTAMP)
        table.add_column(DLabel.STATUS)
        table.add_column(DLabel.OPERATION)
        table.add_column(DLabel.TYPE)
        table.add_column(DLabel.INSTANCE)
        table.add_column(DLabel.MESSAGE)
        table.add_column(DLabel.DETAILS)
        for job in jobs_list:
            date, time = job.updated_at().strftime("%Y-%m-%d %H:%M:%S").split()
            msg_text = job.msg()

            # Break into separate lines
            lines = [line.strip() for line in msg_text.splitlines() if line.strip()]

            for i, line in enumerate(lines):
                if ":" in line:
                    msg, details = line.split(":", 1)
                    msg, details = msg.strip(), details.strip()
                else:
                    msg, details = line.strip(), ""

                # First line gets all job metadata, following lines leave them blank
                if i == 0:
                    table.add_row(
                        f"[b]{date}[/] [b green]{time}[/]",
                        job.status().upper(),
                        f"[b]{job.op().capitalize()}[/]",
                        TYPE_TABLE.get(job.elem_type()),
                        f"[yellow]{job.instance()}[/]",
                        msg,
                        f"[b]{details}[/]" if details else "",
                    )
                else:
                    table.add_row(
                        "", "", "", "", "",  # empty metadata for continuation lines
                        msg,
                        f"[b]{details}[/]" if details else "",
                    )

        self.log_widget.update(table)
        

