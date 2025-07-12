"""
db4e/Messages/Quit.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0

Usage example:
    self.post_message(Quit(self))
"""

from textual.widget import Widget
from textual.message import Message

class Quit(Message):
    def __init__(self, sender: Widget) -> None:
        super().__init__()
        self.sender = sender