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
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import ScrollableContainer, Vertical

from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Modules.Helper import gen_tui_log_table
from db4e.Constants.Fields import (
    PANE_BOX_FIELD, HEALTH_MSGS_FIELD)

class TUILogPane(Static):

    results = Label()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.results = Static()

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                self.results
            ),
            classes=PANE_BOX_FIELD)

    def set_data(self, job_list):
        self.results.update(gen_tui_log_table(job_list=job_list))
        self.post_message(RefreshNavPane(self))
