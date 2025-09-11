"""
db4e/Panes/LogViewPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
import os
import asyncio
from textual.reactive import reactive
from textual.widgets import Static, Label, Log
from textual.containers import Container, ScrollableContainer, Vertical, Horizontal

from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.DForm import DForm
from db4e.Constants.DDef import DDef


class LogViewPane(Container):

    log_lines = reactive([], always_update=True)
    max_lines = DDef.MAX_LOG_LINES
    header = Label("", classes=DForm.FORM_1)
    log_widget = Log(highlight=True, auto_scroll=True, classes=DForm.PANE_BOX)


    def compose(self):    

        yield Vertical(
            self.header,
            ScrollableContainer(
                self.log_widget),
            classes=DForm.PANE_BOX)
        

    def preload(self, path):
        """Return the last num_lines from file at path."""
        if os.path.exists(path):
            with open(path, "rb") as f:
                f.seek(0, os.SEEK_END)
                buffer = bytearray()
                pointer = f.tell()
                lines_found = 0
                while pointer > 0 and lines_found <= DDef.MAX_LOG_LINES:
                    block_size = min(1024, pointer)
                    pointer -= block_size
                    f.seek(pointer)
                    buffer[:0] = f.read(block_size)
                    lines_found = buffer.count(b"\n")
                return buffer.decode(errors="ignore").splitlines()[-DDef.MAX_LOG_LINES:]
        else:
            return ["No log file found"]


    def set_data(self, elem):
        old_lines = self.preload(elem.log_file())
        self.log_widget.clear()
        self.log_widget.write_lines(old_lines)

        self.header.update(f"[b]Log File:[/] {elem.log_file()}")
        if os.path.exists(elem.log_file()):
            initial_size = os.path.getsize(elem.log_file())
        else:
            initial_size = 0
        self.run_worker(self.watch_log(elem.log_file(), last_size=initial_size), exclusive=True)


    async def watch_log(self, path, last_size: int = 0):
        try:
            while True:
                if os.path.exists(path):
                    current_size = os.path.getsize(path)
                    if current_size < last_size:
                        # Log was rotated/truncated
                        last_size = 0
                        self.log_widget.clear()
                    if current_size > last_size:
                        with open(path, "r") as f:
                            f.seek(last_size)
                            lines = [line.rstrip("\n") for line in f]
                            if lines:
                                self.log_widget.write_lines(lines)
                        last_size = current_size
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            return





