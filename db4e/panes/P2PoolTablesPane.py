"""
db4e/Panes/P2PoolTablesPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from rich import box
from rich.table import Table

from textual.reactive import reactive
from textual.widgets import Static, Label
from textual.containers import ScrollableContainer, Vertical

from db4e.Constants.DElem import DElem
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm
from db4e.Constants.DDef import DDef
from db4e.Constants.DField import DField



class P2PoolTablesPane(Static):

    hashrates_table = Static("Missing Data", id="hashrates_table")

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                self.hashrates_table,
            classes=DForm.PANE_BOX)
        )

    def set_data(self, table_data: dict ):
        table = Table(
            title="14 Day Hashrate History",
            show_header=True, header_style="bold #31b8e6", style="#0c323e", 
            box=box.SIMPLE)

        table.add_column(DLabel.XMRIG)
        table.add_column("0")
        table.add_column("1")
        table.add_column("2")
        table.add_column("3")
        table.add_column("4")
        table.add_column("5")
        table.add_column("6")
        table.add_column("7")
        table.add_column("8")
        table.add_column("9")
        table.add_column("10")
        table.add_column("11")
        table.add_column("12")
        table.add_column("13")
        self.hashrates_table.update(content=table)

        

