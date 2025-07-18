"""
db4e/Panes/Welcome.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
from rich import box
from rich.table import Table
from textual.widgets import Label
from textual.containers import Container, ScrollableContainer, Vertical
from textual.app import ComposeResult

from db4e.Constants.Fields import PANE_BOX_FIELD

class Welcome(Container):

    def compose(self) -> ComposeResult:
        

        highlights = Table(title="[cyan b]Db4E Features Today[/]", show_header=True, box=box.SIMPLE, border_style="green", padding=(0, 1))
        highlights.add_column("", width=2, no_wrap=True)
        highlights.add_column("[cyan]Feature[/]", style="bold", no_wrap=True)
        highlights.add_column("[cyan]Description[/]")
        highlights.add_row("🎉", "[green]PyPI Release[/]", "[green]First official PyPI production release — now you can `pip install db4e`![/]")
        highlights.add_row("🛠️", "[green]Deployment Manager[/]", "[green]Smooth vendor directory handling and update workflows.[/]")
        highlights.add_row("🖥️", "[green]Textual TUI[/]", "[green]Fully integrated Textual-based TUI with interactive forms.[/]")
        highlights.add_row("🔒", "[green]Security[/]", "[green]Built-in security architecture with sudoers-based privilege management.[/]")
        highlights.add_row("🧩", "[green]Modular Design[/]", "[green]Future-proof upgrades of Monerod, P2Pool, and XMRig.[/]")
        highlights.add_row("✅", "[green]Git Workflow[/]", "[green]Active development in Git branches, keeping `main` clean and stable.[/]")

        coming = Table(title="[cyan b]Coming Soon[/]", show_header=True, box=box.SIMPLE, border_style="green", padding=(0, 1))
        coming.add_column("", width=2, no_wrap=True)
        coming.add_column("[cyan]Feature[/]", style="bold", no_wrap=True)
        coming.add_column("[cyan]Description[/]")
        coming.add_row("📈", "[green]Historical Data[/]", "[green]Rich historical data tracking for mining performance and yield.[/]")
        coming.add_row("🧙", "[green]Terminal Analytics[/]", "[green]Plotext-based terminal analytics directly in the TUI.[/]")
        coming.add_row("📢", "[green]Version Checker[/]", "[green]PyPI release checking — automatic version notifications.[/]")
        coming.add_row("🔒", "[green]Security Docs[/]", "[green]Full security architecture documentation.[/]")
        coming.add_row("🐞", "[green]Testing + CI/CD[/]", "[green]Full unit + integration testing suite and CI/CD integration.[/]")
        coming.add_row("🕵️", "[green]Community[/]", "[green]Community building and open contributions — feedback welcomed![/]")

        yield Vertical(
            ScrollableContainer (
                Label(highlights),
                Label(coming),
                classes=PANE_BOX_FIELD,
            )
        )
        
