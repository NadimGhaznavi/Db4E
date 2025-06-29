# db4e/Status/NodeStatusBar.py

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Label

class TopBar(Container):
    hostname = reactive("", init=False, always_update=True)
    status_msg = reactive("", init=False, always_update=True)

    def __init__(self, host="", app_version="", help="press [b highlight]?[/b highlight] for commands"):
        super().__init__()

        self.app_title = Text.from_markup(f"[b green]Db4E[/b green] [dim]v{app_version}[/dim]")
        self.topbar_title = Label(self.app_title, id="topbar_title")

        self.topbar_host = Label("", id="topbar_host")
        self.topbar_help = Label(Text.from_markup(help), id="topbar_help")

        self.hostname = host
        self.status_msg = ""

    def _update_topbar_host(self):
        if self.hostname or self.status_msg:
            self.topbar_host.update(
                Text.from_markup(f"[b cyan]{self.hostname}[/b cyan] {self.status_msg}")
            )
        else:
            self.topbar_host.update("")

    def watch_hostname(self):
        self._update_topbar_host()

    def watch_status_msg(self):
        self._update_topbar_host()

    def compose(self) -> ComposeResult:
        yield self.topbar_title
        yield self.topbar_host
        yield self.topbar_help
