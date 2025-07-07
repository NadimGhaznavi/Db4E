"""
db4e/Widgets/Clock.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from datetime import datetime
from textual.widgets import Label
from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.containers import Container

class Clock(Container):

    cur_datetime = reactive('')
    emoji_index = reactive('0')
    label = Label('', id="clock")

    CLOCK_EMOJIS = [
        "🕐", "🕑", "🕒", "🕓", "🕔", "🕕",
        "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"
    ]

    def compose(self) -> ComposeResult:
        yield self.label

    def on_mount(self) -> None:
        self.set_interval(60, self.update_time)
        self.update_time()

    def update_time(self) -> None:
        self.emoji_index = (int(self.emoji_index) + 1) % len(self.CLOCK_EMOJIS)
        self.cur_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

    def watch_cur_datetime(self, time: str) -> None:
        emoji = self.CLOCK_EMOJIS[self.emoji_index]
        self.label.update(f"{emoji} {time}")