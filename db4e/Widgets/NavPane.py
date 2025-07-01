"""
db4e/Widgets/NavPane.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

from textual.widgets import Label
from textual.app import ComposeResult
from textual.containers import Container

class NavPane(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Label('NavBar', id="navbar")