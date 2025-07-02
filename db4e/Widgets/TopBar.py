"""
db4e/Widgets/TopBar.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Label

class TopBar(Container):
    tb_component = reactive("", init=False, always_update=True)
    tb_msg = reactive("", init=False, always_update=True)

    def __init__(self, sender = "", component: str = "", msg: str = "", app_version: str ="", **kwargs):
        super().__init__(**kwargs)
        self.sender = sender
        self.component = component
        self.msg = msg

        self.topbar_title = Text.from_markup(f"[b green]Db4E[/b green] [dim]v{app_version}[/dim]")
        self.topbar_component = Label("")

    def update_topbar(self):
        if self.tb_component or self.tb_msg:
            self.topbar_component.update(
                Text.from_markup(f"[b cyan]{self.tb_component} - {self.tb_msg}[/b cyan]")
            )
        else:
            self.topbar_component.update("")

    def set_component(self, component):
        self.tb_component = component

    def set_msg(self, msg):
        self.tb_msg = msg

    def watch_tb_component(self):
        self.update_topbar()

    def watch_tb_msg(self):
        self.update_topbar()

    def compose(self) -> ComposeResult:
        with Horizontal(id="topbar"):
            yield Label((self.topbar_title), id="topbar_title")
            yield self.topbar_component

