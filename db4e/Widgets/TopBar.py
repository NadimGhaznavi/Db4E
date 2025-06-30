# db4e/Widgets/TopBar.py

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Label

class TopBar(Container):
    tb_component = reactive("", init=False, always_update=True)
    tb_msg = reactive("", init=False, always_update=True)

    def __init__(self, component="", app_version=""):
        super().__init__()

        self.topbar_title = Text.from_markup(f"[b green]Db4E[/b green] [dim]v{app_version}[/dim]", id="topbar_title")
        self.topbar_component = Label("", id="topbar_component")

    def _update_topbar(self):
        if self.tb_component or self.tb_msg:
            self.topbar_component.update(
                Text.from_markup(f"[b cyan]{self.tb_component}[/b cyan] {self.tb_msg}")
            )
        else:
            self.topbar_component.update("")

    def set_component(self, component):
        self.tb_component = component

    def set_msg(self, msg):
        self.tb_msg = msg

    def watch_tb_component(self):
        self._update_topbar_component()

    def watch_tb_msg(self):
        self._update_topbar_component()

    def compose(self) -> ComposeResult:
        with Horizontal(id="topbar"):
            yield self.topbar_title
            yield self.topbar_component
