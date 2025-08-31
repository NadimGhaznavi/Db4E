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
from textual.widgets import Static, Label
from textual.containers import Container, ScrollableContainer, Vertical, Horizontal

from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import (
    PANE_BOX_FIELD, STATIC_CONTENT_FIELD, FORM_1_FIELD)
from db4e.Constants.Defaults import (
    MAX_LOG_LINES_DEFAULT)


class LogViewPane(Container):

    log_lines = reactive([], always_update=True)
    max_lines = MAX_LOG_LINES_DEFAULT
    queue = asyncio.Queue()
    header = Label("", classes=FORM_1_FIELD)
    log_lines_widget = Label("", classes=PANE_BOX_FIELD)


    def compose(self):    

        yield Vertical(
            self.header,
            ScrollableContainer(
                self.log_lines_widget),
            classes=PANE_BOX_FIELD)
        

    def check_queue(self):
        while not self.queue.empty():
            line = self.queue.get_nowait()
            print(f"LogViewPane:check_queue(): line: {line}")
            self.log_lines.append(line)
            if len(self.log_lines) > self.max_lines:
                self.log_lines.pop(0)
        self.log_lines_widget.update("\n".join(self.log_lines))


    def preload(self, path):
        """Return the last num_lines from file at path."""
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            buffer = bytearray()
            pointer = f.tell()
            lines_found = 0
            while pointer > 0 and lines_found <= MAX_LOG_LINES_DEFAULT:
                block_size = min(1024, pointer)
                pointer -= block_size
                f.seek(pointer)
                buffer[:0] = f.read(block_size)
                lines_found = buffer.count(b"\n")
            return buffer.decode(errors="ignore").splitlines()[-MAX_LOG_LINES_DEFAULT:]


    def set_data(self, elem):
        self.log_lines = self.preload(elem.log_file())
        self.log_lines_widget.update("\n".join(self.log_lines))

        self.header.update(f"[b]Log File:[/] {elem.log_file()}")
        self.run_worker(self.watch_log(elem.log_file()), exclusive=True)
        self.set_interval(1, self.check_queue)


    async def watch_log(self, path):
        with open(path, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    await self.queue.put(line.strip())
                else:
                    await asyncio.sleep(1)

