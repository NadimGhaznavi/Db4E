""" lib/components/detail_pane.py"""

from textual.widgets import Static, Label
from textual.app import ComposeResult
from textual.widget import Widget
from textual.containers import Horizontal, Vertical

class DetailPane(Widget):

    def compose(self) -> ComposeResult:
        yield Static("Select an item from the menu to view details.", id="detail_pane")
        
        

