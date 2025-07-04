"""
db4e/Panes/InstallResults.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
from rich import box
from rich.table import Table
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container

from db4e.Messages.RefreshNavPane import RefreshNavPane

class InstallResults(Container):

    def set_data(self, task_list):

        table = Table(show_header=True, header_style="bold cyan", style="bold green", box=box.SIMPLE)
        table.add_column("Component", width=25)
        table.add_column("Message")

        for task in task_list:
            for category, msg_dict in task.items():
                message = msg_dict["msg"]
                if msg_dict["status"] == "good":
                    table.add_row(f"✅ [green]{category}[/]", f"[green]{message}[/]")
                elif msg_dict["status"] == "warn":
                    table.add_row(f"⚠️  [yellow]{category}[/]", f"[yellow]{message}[/]")
                elif msg_dict["status"] == "error":
                    table.add_row(f"💥 [red]{category}[/]", f"[red]{message}[/]")

        self.mount(Static(table))
        self.app.post_message(RefreshNavPane(self))
