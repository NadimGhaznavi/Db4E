"""
db4e/Messages/Db4eMsg.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.widget import Widget
from textual.message import Message

class Db4eMsg(Message):
    def __init__(self, sender: Widget, form_data: dict) -> None:
        super().__init__()
        self.form_data = form_data
