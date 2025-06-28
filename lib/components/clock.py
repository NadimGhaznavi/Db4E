"""lib/components/clock.py"""

from datetime import datetime
from textual.widgets import Label
from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive

class Clock(Widget):

    cur_datetime = reactive('')
    label = Label('', id="clock")

    def compose(self) -> ComposeResult:
        yield self.label

    def on_mount(self) -> None:
        self.set_interval(60, self.update_time)
        self.update_time()

    def update_time(self) -> None:
        self.cur_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

    def watch_cur_datetime(self, time: str) -> None:
        self.label.update(time)