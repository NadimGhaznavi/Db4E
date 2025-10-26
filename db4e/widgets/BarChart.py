"""
db4e/Modules/HashratePlot.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from typing import Any

from textual.widgets import Select
from textual_plot import PlotWidget, HiResMode

from db4e.Constants.DLabel import DLabel



# Hashrate data is collected once per hour
ONE_WEEK = 7 * 24

class BarChart(PlotWidget):
    """
    A bar chart widget.
    """

    def __init__(self, title, id):
        super().__init__(title, id, allow_pan_and_zoom=False)
        self._barchart_id = id
        self._all_days = None
        self._all_values = None
        self.set_xlabel(DLabel.DAYS)
        self.set_ylabel(DLabel.BLOCKS_FOUND)


    def load_data(self, days, blocks_found):
        self._all_days = days
        self._all_values = blocks_found


    def barchart_plot(self, days=None, values=None) -> None:
        if days is not None and values is not None:
            plot_days = days
            plot_values = values
        else:
            plot_days = self._all_days
            plot_values = self._all_values

        plot_days, plot_values = self.regen_data(plot_days, plot_values)
        self.clear()
        self.plot(x=plot_days, y=plot_values, hires_mode=HiResMode.BRAILLE)


    def regen_data(self, days, values):
        new_days = []
        for x in days:
            new_days.extend([x + 0, x + 0.1, x + 0.101])
            new_days.extend([x + 0.898, x + 0.899, x + 0.9])

        new_values = []
        for y in values:
            new_values.extend([0, 0, y, y, 0, 0])
        return new_days, new_values
    

        
    