"""
db4e/Panes/Results.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from rich import box
from rich.table import Table
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import ScrollableContainer, Vertical

from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import (
    GOOD_FIELD, MESSAGE_FIELD, PANE_BOX_FIELD, STATUS_FIELD, WARN_FIELD, ERROR_FIELD)

class Results(Static):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.results = Static()

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                self.results
            ),
            classes=PANE_BOX_FIELD)

    def set_data(self, task_list):

        table = Table(show_header=True, header_style="bold cyan", style="bold green", 
                      box=box.SIMPLE)
        table.add_column("Component", width=25)
        table.add_column("Message")

        for task in task_list:
            for category, msg_dict in task.items():
                message = msg_dict[MESSAGE_FIELD]
                if msg_dict[STATUS_FIELD] == GOOD_FIELD:
                    table.add_row(f"✅ [green]{category}[/]", f"[green]{message}[/]")
                elif msg_dict[STATUS_FIELD] == WARN_FIELD:
                    table.add_row(f"⚠️  [yellow]{category}[/]", f"[yellow]{message}[/]")
                elif msg_dict[STATUS_FIELD] == ERROR_FIELD:
                    table.add_row(f"💥 [bold yellow]{category}[/]", 
                                  f"[bold yellow]{message}[/]")

        self.results.remove_children()
        self.results.update(table)
        self.app.post_message(RefreshNavPane(self))
