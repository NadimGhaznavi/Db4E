# db4e/Status/NodeStatusBar.py

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Label

class TopBar(Container):
    component = reactive("", init=False, always_update=True)
    status_msg = reactive("", init=False, always_update=True)

    def __init__(self, component="", app_version="", help="press [b highlight]?[/b highlight] for commands"):
        super().__init__()

        self.app_title = Text.from_markup(f"[b green]Db4E[/b green] [dim]v{app_version}[/dim]")
        self.topbar_title = Label(self.app_title, id="topbar_title")

        self.topbar_component = Label("", id="topbar_component")
        self.topbar_help = Label(Text.from_markup(help), id="topbar_help")

        self.component = component
        self.status_msg = ""

    def _update_topbar_component(self):
        if self.component or self.status_msg:
            self.topbar_component.update(
                Text.from_markup(f"[b cyan]{self.component}[/b cyan] {self.status_msg}")
            )
        else:
            self.topbar_component.update("")

    def watch_component(self):
        self._update_topbar_component()

    def watch_status_msg(self):
        self._update_topbar_component()

    def compose(self) -> ComposeResult:
        with Horizontal(id="topbar_row"):
            yield self.topbar_title
            yield self.topbar_component
            yield self.topbar_help
