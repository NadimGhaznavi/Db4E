"""
db4e/Panes/RuntimePane.py

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
from db4e.Constants.DOps import DOps



class RuntimePane(Static):

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
        table.add_column(DLabel.ELEMENT_TYPE)
        table.add_column(f"[yellow]{DLabel.INSTANCE}[/]")
        table.add_column("", justify=DField.RIGHT, width=8),
        table.add_column(DLabel.CURRENT, justify=DField.RIGHT)
        table.add_column("", justify=DField.RIGHT, width=8),
        table.add_column(f"[green]{DLabel.TOTAL}[/]", justify=DField.RIGHT)

        for event in events:
            # Split current uptime day(s) and hours:minutes:seconds
            if "," in event[DOps.CURRENT_UPTIME]:
                cur_days, cur_time = event[DOps.CURRENT_UPTIME].split(",")
            else:
                cur_days = ""
                cur_time = event[DOps.CURRENT_UPTIME]

            # Same split for total uptime
            if "," in event[DOps.TOTAL_UPTIME]:
                total_days, total_time = event[DOps.TOTAL_UPTIME].split(",")
            else:
                total_days = ""
                total_time = event[DOps.TOTAL_UPTIME]

            table.add_row(
                f"[b]{event[DMongo.ELEMENT_TYPE]}[/]",
                f"[yellow]{event[DMongo.INSTANCE]}[/]",
                f"[cyan]{cur_days}[/]",
                f"[cyan]{cur_time}[/]",
                f"[green]{total_days}[/]",
                f"[green]{total_time}[/]"
            )
        self.uptime_data.update(table)
        
        
