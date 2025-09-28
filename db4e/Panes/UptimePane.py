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

from textual.reactive import reactive
from textual.widgets import Static
from textual.containers import ScrollableContainer, Vertical

from db4e.Constants.DElem import DElem
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm
from db4e.Constants.DDef import DDef
from db4e.Constants.DField import DField



class UptimePane(Static):


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.results = Static()

    def compose(self):
        yield Vertical(
            ScrollableContainer(
                Static(DLabel.UPTIME)
            ),
            classes=DForm.PANE_BOX)

    def set_data(self, elem):
        pass
        
