""" lib/DetailPane/DetailPane.py"""

from textual.widgets import Static
from textual.app import ComposeResult
from textual.widget import Widget

class DetailPane(Widget):
    def compose(self) -> ComposeResult:
        yield Static("Select an item from the menu to view details.")