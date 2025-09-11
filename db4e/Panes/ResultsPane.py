"""
db4e/Panes/ResultsPane.py

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
from db4e.Modules.Helper import gen_results_table
from db4e.Constants.DForm import DForm



class ResultsPane(Static):

    results = Label()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.results = Static()

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                self.results
            ),
            classes=DForm.PANE_BOX)

    def set_data(self, elem):
        msgs = elem.pop_msgs()
        self.results.update(gen_results_table(results=msgs))
        self.post_message(RefreshNavPane(self))
