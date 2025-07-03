"""
db4e/Panes/InstallResults.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

from textual.app import ComposeResult
from textual.widgets import Label
from textual.containers import Container
from textual.message import Message

class InstallResults(Container):

    def __init__(self, id: str, data=None):
        super().__init__(id=id)
        self.data = data

    def set_data(self, data):
        self.data = data
        self.refresh()

    def compose(self) -> ComposeResult:
        yield Label('Install Results')
        print(self.data)
