"""
db4e/Panes/XMRigAnalyticsPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Label

from db4e.Modules.P2Pool import P2Pool

from db4e.Widgets.HashratePlot import HashratePlot

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm



class XMRigAnalyticsPane(Container):


    def compose(self):

        INTRO = f"View analytics information about the [cyan]{DLabel.XMRIG}[/] deployment here."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    HashratePlot("Hashrate", id="hashrate_plot")
                ),
                classes=DForm.PANE_BOX))


    def set_data(self, p2pool: P2Pool):
        hashrate_plot = self.query_one("#hashrate_plot")
        hashrate_plot.update(p2pool.hashrates())