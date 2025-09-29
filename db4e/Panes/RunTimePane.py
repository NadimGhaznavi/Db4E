"""
db4e/Panes/UptimePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from rich import box
from rich.table import Table

from textual.widgets import Static
from textual.containers import ScrollableContainer, Vertical

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm
from db4e.Constants.DField import DField
from db4e.Constants.DMongo import DMongo



class RunTimePane(Static):

    uptime_data = Static("Missing Data", id="events")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.results = Static()

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                self.uptime_data,
            ),
            classes=DForm.PANE_BOX)

    def set_data(self, events):
        table = Table(show_header=True, header_style="bold #31b8e6", style="#0c323e", box=box.SIMPLE)
        table.add_column(DLabel.TIMESTAMP)
        table.add_column(DLabel.ELEMENT_TYPE)
        table.add_column(DLabel.INSTANCE)
        table.add_column(DLabel.CURRENT_UPTIME)
        table.add_column(DLabel.TOTAL_UPTIME)

        for row in events:
            table.add_row(
                row[DMongo.TIMESTAMP],
                row[DMongo.ELEM_TYPE],
                row[DMongo.INSTANCE],
                row[DField.CURRENT_UPTIME],
                row[DField.TOTAL_UPTIME]
            )
        self.uptime_data.update(table)
        
        
