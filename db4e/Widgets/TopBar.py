"""
db4e/Widgets/TopBar.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""

from dataclasses import dataclass

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Label

@dataclass
class TopBarState:
    title: str = ""
    sub_title: str = ""

hi = "#31b8e6"

class TopBar(Container):
    tb_state = reactive(TopBarState(), always_update=True)

    def __init__(self, sender = "", title: str = "", sub_title: str = "", app_version: str ="", **kwargs):
        super().__init__(**kwargs)
        self.sender = sender
        self.tb_version = Label(Text.from_markup(f"[b {hi}]Db4E[/] v[{hi}]{app_version}[/]"), id="topbar_version")
        self.tb_title = Label(Text.from_markup(f"[b {hi}]{title} - {sub_title}[/]"), id="topbar_title")

    def set_state(self, title: str, sub_title: str):
        self.tb_state = TopBarState(title, sub_title)

    def watch_tb_state(self, old: TopBarState, new: TopBarState) -> None:
        self.tb_title.update(
            Text.from_markup(f"[b {hi}]{self.tb_state.title}[/] - [{hi}]{self.tb_state.sub_title}[/]")
            #Text('[Title - SubTitle]')
        )

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.tb_version
            yield self.tb_title

