"""
db4e/Messages/SwitchPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0

Usage example: 
    await self.post_message(SwitchPane(self, "InstallResults", results))
"""

from textual.widget import Widget
from textual.message import Message

class SwitchPane(Message):
    def __init__(self, sender: Widget, pane_name: str, data: dict = None):
        super().__init__()
        self.pane_name = str(pane_name)
        self.data = data

