"""
db4e/Panes/TUILogPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from rich import box
from rich.syntax import Syntax
from rich.table import Table

from textual.reactive import reactive
from textual.widgets import Static, Log, RichLog
from textual.containers import ScrollableContainer, Vertical

from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import (
    PANE_BOX_FIELD, MONEROD_FIELD, MONEROD_REMOTE_FIELD,
    P2POOL_FIELD, P2POOL_REMOTE_FIELD, XMRIG_FIELD)
from db4e.Constants.Labels import (
    MONEROD_SHORT_LABEL, P2POOL_SHORT_LABEL, XMRIG_SHORT_LABEL)
from db4e.Constants.Defaults import (
    MAX_LOG_LINES_DEFAULT)

TYPE_TABLE = {
    MONEROD_FIELD: MONEROD_SHORT_LABEL,
    MONEROD_REMOTE_FIELD: MONEROD_SHORT_LABEL,
    P2POOL_FIELD: P2POOL_SHORT_LABEL,
    P2POOL_REMOTE_FIELD: P2POOL_SHORT_LABEL,
    XMRIG_FIELD: XMRIG_SHORT_LABEL,
}

class TUILogPane(Static):

    log_lines = reactive([], always_update=True)
    max_lines = MAX_LOG_LINES_DEFAULT
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
            classes=PANE_BOX_FIELD)

    def set_data(self, job_list):
        #self.log_widget.clear()
        table = Table(show_header=True, header_style="bold #31b8e6", style="#0c323e", box=box.SIMPLE)
        table.add_column("Timestamp")
        table.add_column("Status")
        table.add_column("Operation")
        table.add_column("Type")
        table.add_column("Instance")
        table.add_column("Message")
        table.add_column("Details")
        for job in job_list:
            date, time = job.updated_at().strftime("%Y-%m-%d %H:%M:%S").split()

            if ":" in job.msg():
                msg, details = job.msg().split(":")
                details = f"[b]{details}[/]"
            else:
                msg = job.msg()
                details = ""

            table.add_row(
                str(f"[b]{date}[/] [b green]{time}[/]"),
                str(job.status()).upper(),
                str(f"[b]{job.op().capitalize()}[/]"),
                str(TYPE_TABLE.get(job.elem_type())),
                str(f"[yellow]{job.instance()}[/]"),
                msg,
                details,
            )
        self.log_widget.update(table)
        

