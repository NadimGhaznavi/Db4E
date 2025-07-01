"""
db4e/Widgets/DetailPane.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

from textual.app import App, ComposeResult
from textual.widgets import ContentSwitcher
from textual.reactive import reactive
from textual.containers import Container

from db4e.Modules.PaneMgr import PaneMgr


class DetailPane(Container):

    pane_id = reactive('Welcome')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pane_manager = PaneMgr()

    def compose(self) -> ComposeResult:
        print(f'DetailPane:compose() - {self.pane_id}')
        yield self.pane_manager.get_pane(self.pane_id)

    def set_pane_id(self, pane_id):
        self.pane_id = pane_id

    def watch_pane_id(self):
        self.compose()    
