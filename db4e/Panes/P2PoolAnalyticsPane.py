"""
db4e/Panes/P2PoolAnalyticsPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label

from db4e.Modules.P2Pool import P2Pool

from db4e.Widgets.HashratePlot import HashratePlot

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm



class P2PoolAnalyticsPane(Container):

    intro_label = Label("", classes=DForm.INTRO)
    instance_label = Label("", id="instance_label",classes=DForm.STATIC)
    hashrate_label = Label("", id="hashrate_label", classes=DForm.STATIC)

    def compose(self):

        yield Vertical(
            ScrollableContainer(
                self.intro_label,

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_15),
                        self.instance_label),
                    Horizontal(
                        Label(DLabel.HASHRATE, classes=DForm.FORM_LABEL_15),
                        self.hashrate_label),
                    classes=DForm.FORM_2),                 

                Vertical(
                    HashratePlot("Hashrate", id="hashrate_plot"),
                    classes=DForm.PANE_BOX
                ),
                classes=DForm.PANE_BOX))


    def set_data(self, p2pool: P2Pool):
        hashrate_plot = self.query_one("#hashrate_plot")
        hashrate_plot.update(p2pool.hashrates())
        INTRO = f"View analytics information for the " \
            f"[cyan]{p2pool.instance()} {DLabel.P2POOL}[/] deployment."
        self.intro_label.update(INTRO)
        self.instance_label.update(p2pool.instance())
        self.hashrate_label.update(str(p2pool.hashrate()))


