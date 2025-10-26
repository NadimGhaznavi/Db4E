"""
db4e/Messages/UpdateTopBar.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0

Usage example:
    self.post_message(UpdateTopBar(self, "Database 4 Everything ", "Welcome"))
"""

from textual.widget import Widget
from textual.message import Message

class UpdateTopBar(Message):
    def __init__(self, sender: Widget, title: str, sub_title: str) -> None:
        super().__init__()
        self.title = title
        self.sub_title = sub_title
