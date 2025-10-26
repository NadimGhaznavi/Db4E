"""
db4e/Widgets/SharesFoundPlot.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

import math

from textual_plot import PlotWidget, HiResMode
from textual.app import ComposeResult, Widget

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DForm import DForm


class SharesFoundPlot(Widget):

    days = []
    values = []

    def compose(self):
        yield PlotWidget()

    def plot(self, days, values):
        plot = self.query_one(PlotWidget)
        plot.clear()
        plot.plot(x=days, y=values, hires_mode=HiResMode.BRAILLE, line_style="green")

    def on_mount(self):
        plot = self.query_one(PlotWidget)
        plot.set_xlabel(DLabel.DAYS)
        plot.set_ylabel(DLabel.SHARES_FOUND)

    def found_shares_plot(self, selected_time: str):
        # No data
        if not self.days or not self.values:
            return

        # There isn't enough data for the selected time range
        elif len(self.days) < selected_time:
            self.plot(self.days, self.values)

        # A value of -1 is a flag to indicate all available data
        elif selected_time == -1:
            self.plot(self.days, self.values)

        # Slice a segment of the available data for plotting
        else:
            new_days = self.days[-selected_time:]
            new_values = self.values[-selected_time:]
            self.plot(new_days, new_values)

    def load_data(self, days, values):
        self.days = days
        self.values = values
