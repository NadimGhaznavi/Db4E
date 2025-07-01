from textual.widgets import Label
from textual.containers import Container
from textual.app import ComposeResult



class Welcome(Container):

    def compose(self) -> ComposeResult:
        yield Label('Welcome Pane')
        