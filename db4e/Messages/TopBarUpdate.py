"""
db4e/Messages/TopBarUpdate.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

from textual.message import Message

class TopBarUpdate(Message):
    def __init__(self, sender, component: str, msg: str):
        super().__init()
        self.sender = sender
        self.component = component
        self.msg = msg