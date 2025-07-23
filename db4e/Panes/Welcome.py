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

color = "#9cae41"

class Welcome(Container):

    def compose(self) -> ComposeResult:
        

        highlights = Table(title="[#31b8e6 b]Db4E Features Today[/]", show_header=True, box=box.SIMPLE, border_style="#67732a", padding=(0, 1))
        highlights.add_column("", width=2, no_wrap=True)
        highlights.add_column("[#31b8e6]Feature[/]", style="bold", no_wrap=True)
        highlights.add_column("[#31b8e6]Description[/]")
        highlights.add_row("🎉", "[#9cae41]PyPI Release[/]", "[#9cae41]First official PyPI production release — now you can `pip install db4e`![/]")
        highlights.add_row("🛠️", "[#9cae41]Deployment Manager[/]", "[#9cae41]Smooth vendor directory handling and update workflows.[/]")
        highlights.add_row("🖥️", "[#9cae41]Textual TUI[/]", "[#9cae41]Fully integrated Textual-based TUI with interactive forms.[/]")
        highlights.add_row("🔒", "[#9cae41]Security[/]", "[#9cae41]Built-in security architecture with sudoers-based privilege management.[/]")
        highlights.add_row("🧩", "[#9cae41]Modular Design[/]", "[#9cae41]Future-proof upgrades of Monerod, P2Pool, and XMRig.[/]")
        highlights.add_row("✅", "[#9cae41]Git Workflow[/]", "[#9cae41]Active development in Git branches, keeping `main` clean and stable.[/]")

        coming = Table(title="[#31b8e6 b]Coming Soon[/]", show_header=True, box=box.SIMPLE, border_style="#67732a", padding=(0, 1))
        coming.add_column("", width=2, no_wrap=True)
        coming.add_column("[#31b8e6]Feature[/]", style="bold", no_wrap=True)
        coming.add_column("[#31b8e6]Description[/]")
        coming.add_row("📈", "[#9cae41]Historical Data[/]", "[#9cae41]Rich historical data tracking for mining performance and yield.[/]")
        coming.add_row("🧙", "[#9cae41]Terminal Analytics[/]", "[#9cae41]Plotext-based terminal analytics directly in the TUI.[/]")
        coming.add_row("📢", "[#9cae41]Version Checker[/]", "[#9cae41]PyPI release checking — automatic version notifications.[/]")
        coming.add_row("🔒", "[#9cae41]Security Docs[/]", "[#9cae41]Full security architecture documentation.[/]")
        coming.add_row("🐞", "[#9cae41]Testing + CI/CD[/]", "[#9cae41]Full unit + integration testing suite and CI/CD integration.[/]")
        coming.add_row("🕵️", "[#9cae41]Community[/]", "[#9cae41]Community building and open contributions — feedback welcomed![/]")

        yield Vertical(
            ScrollableContainer (
                Label(highlights),
                Label(coming),
                classes=PANE_BOX_FIELD,
            )
        )
        
