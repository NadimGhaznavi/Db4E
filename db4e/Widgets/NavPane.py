# db4e/Widgets/NavPane.py

from textual.widgets import Label
from textual.app import ComposeResult
from textual.containers import Container

class NavPane(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Label('NavBar', id="navbar")