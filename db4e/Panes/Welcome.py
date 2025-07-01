"""
db4e/Panes/Welcome.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from textual.widgets import Label, Static
from textual.containers import Container
from textual.app import ComposeResult

from db4e.Widgets.TopBar import TopBar

class Welcome(Container):

    def compose(self) -> ComposeResult:
        print(f'Welcome:compose()')
        yield Label('Welcome Pane')
        yield Static('Welcome Pane - Static')