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

class HashratePlot(PlotWidget):
    """
    A widget for plotting hashrate data.
    """

    def __init__(self, title, id):
        super().__init__(title, id, allow_pan_and_zoom=False)
        self._hashrate_id = id
        self._all_days = None
        self._all_values = None
        self._title = title
        self.set_xlabel(DLabel.DAYS)        


    def load_data(self, days, hashrates, units):
        self._all_days = days
        self._all_values = hashrates
        self.set_ylabel(self._title + " (" + units + ")")


    def hashrate_plot(self, days=None, values=None) -> None:
        if days is not None and values is not None:
            plot_days = days
            plot_values = values
        else:
            plot_days = self._all_days
            plot_values = self._all_values
        self.clear()
        reduced_days, reduced_values = self.reduce_data(plot_days, plot_values)
        self.plot(x=reduced_days, y=reduced_values, hires_mode=HiResMode.BRAILLE)


    def reduce_data(self, times, values):
        # Reduce the total number of data points, otherwise the plot gets "blurry"
        step = max(1, len(times) // ONE_WEEK)

        # Reduce times with step
        reduced_times = times[::step]

        # Bin values by step (average)
        reduced_values = [
            sum(values[i:i+step]) / len(values[i:i+step])
            for i in range(0, len(values), step)
        ]
        return reduced_times[:len(reduced_values)], reduced_values
    

    def update_time_range(self, selected_time):
        if selected_time == -1:
            return

        selected_time = int(selected_time)
        max_length = len(self._all_days)
        if selected_time > max_length:
            selected_time = max_length
        new_values = self._all_values[-selected_time:]
        new_times = self._all_days[-selected_time:]
        self.hashrate_plot(new_times, new_values)



