"""
db4e/Panes/XMRigAnalyticsPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label

from db4e.Modules.XMRig import XMRig

from db4e.Widgets.HashratePlot import HashratePlot

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm



class XMRigAnalyticsPane(Container):

    instance_label = Label("", id="instance_label",classes=DForm.STATIC)
    hashrate_label = Label("", id="hashrate_label", classes=DForm.STATIC)
    uptime_label = Label("", id="uptime_label", classes=DForm.STATIC)

    def compose(self):

        INTRO = f"View analytics information about the [cyan]{DLabel.XMRIG}[/] deployment here."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        self.instance_label),
                    Horizontal(
                        Label(DLabel.HASHRATE, classes=DForm.FORM_LABEL),
                        self.hashrate_label),
                    Horizontal(
                        Label(DLabel.UPTIME, classes=DForm.FORM_LABEL),
                        self.uptime_label),
                    classes=DForm.FORM_3, id="form_field"),

                Vertical(
                    HashratePlot("Hashrate", id="hashrate_plot")
                ),
                classes=DForm.PANE_BOX))


    def set_data(self, xmrig: XMRig):
        self.instance_label.update(xmrig.instance())
        self.hashrate_label.update(str(xmrig.hashrate()) + " H/s")
        self.uptime_label.update(xmrig.uptime())

        hashrate_plot = self.query_one("#hashrate_plot")
        hashrate_plot.update(xmrig.hashrates())