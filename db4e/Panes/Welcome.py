"""
db4e/Panes/Welcome.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from rich import box
from rich.table import Table
from textual.widgets import Label
from textual.containers import Container, ScrollableContainer, Vertical
from textual.app import ComposeResult

from db4e.Constants.Fields import PANE_BOX_FIELD

color = "#31b8e6"

class Welcome(Container):

    def compose(self) -> ComposeResult:
        

        highlights = Table(title="[cyan b]Db4E Features Today[/]", show_header=True, box=box.SIMPLE, border_style="#0c323e", padding=(0, 1))
        highlights.add_column("", width=2, no_wrap=True)
        highlights.add_column("[cyan]Feature[/]", style="bold", no_wrap=True)
        highlights.add_column("[cyan]Description[/]")
        highlights.add_row("🎉", "[#31b8e6]PyPI Release[/]", "[#31b8e6]First official PyPI production release — now you can `pip install db4e`![/]")
        highlights.add_row("🛠️", "[#31b8e6]Deployment Manager[/]", "[#31b8e6]Smooth vendor directory handling and update workflows.[/]")
        highlights.add_row("🖥️", "[#31b8e6]Textual TUI[/]", "[#31b8e6]Fully integrated Textual-based TUI with interactive forms.[/]")
        highlights.add_row("🔒", "[#31b8e6]Security[/]", "[#31b8e6]Built-in security architecture with sudoers-based privilege management.[/]")
        highlights.add_row("🧩", "[#31b8e6]Modular Design[/]", "[#31b8e6]Future-proof upgrades of Monerod, P2Pool, and XMRig.[/]")
        highlights.add_row("✅", "[#31b8e6]Git Workflow[/]", "[#31b8e6]Active development in Git branches, keeping `main` clean and stable.[/]")

        coming = Table(title="[cyan b]Coming Soon[/]", show_header=True, box=box.SIMPLE, border_style="#0c323e", padding=(0, 1))
        coming.add_column("", width=2, no_wrap=True)
        coming.add_column("[cyan]Feature[/]", style="bold", no_wrap=True)
        coming.add_column("[cyan]Description[/]")
        coming.add_row("📈", "[#31b8e6]Historical Data[/]", "[#31b8e6]Rich historical data tracking for mining performance and yield.[/]")
        coming.add_row("🧙", "[#31b8e6]Terminal Analytics[/]", "[#31b8e6]Plotext-based terminal analytics directly in the TUI.[/]")
        coming.add_row("📢", "[#31b8e6]Version Checker[/]", "[#31b8e6]PyPI release checking — automatic version notifications.[/]")
        coming.add_row("🔒", "[#31b8e6]Security Docs[/]", "[#31b8e6]Full security architecture documentation.[/]")
        coming.add_row("🐞", "[#31b8e6]Testing + CI/CD[/]", "[#31b8e6]Full unit + integration testing suite and CI/CD integration.[/]")
        coming.add_row("🕵️", "[#31b8e6]Community[/]", "[#31b8e6]Community building and open contributions — feedback welcomed![/]")

        yield Vertical(
            ScrollableContainer (
                Label(highlights),
                Label(coming),
                classes=PANE_BOX_FIELD,
            )
        )
        
