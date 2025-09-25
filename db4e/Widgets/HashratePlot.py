"""
db4e/Modules/HashratePlot.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from typing import Any

from textual_plotext import PlotextPlot

# Hashrate data is collected once per hour
ONE_WEEK = 7 * 24

class HashratePlot(PlotextPlot):
    """
    A widget for plotting hashrate data.
    """

    def __init__(
        self,
        title: str,
        *,
        name: str | None = None,
        id: str | None = None,  # pylint:disable=redefined-builtin
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._title = title
        self._unit = "Loading..."
        self._data: list[float] = []
        self._time: list[str] = []

    def hashrate_data(self, hashrate_data=None):
        if hashrate_data is not None:
            self._hashrate_data = hashrate_data
        return self._hashrate_data
    
    def times(self, times=None):
        if times is not None:
            self._times = times
        return self._times
    

    def on_mount(self) -> None:
        """Plot the data using Plotext."""
        self.plt.clear_data()
        self.plt.date_form("Y-m-d H:M")
        self.plt.title(self._title)
        self.plt.xlabel("Time")
        self.plt.ylabel(self._unit)
        self.plt.canvas_color("black")


    def load_all_data(self, hashrate_data: dict[str, Any]) -> None:
        """Load the hashrate data"""
        self.hashrate_data(hashrate_data["values"])
        self.times(hashrate_data["times"])
        self.units(hashrate_data["units"])


    def plot(self) -> None:
        """Redraw the plot."""
        self.plt.clear_data()
        self.plt.ylabel(self._unit)
        self.plt.plot(self._time, self._data, marker="braille")
        self.refresh()


    def reduce_data(self, times, values, max_points=ONE_WEEK):
        # Reduce the total number of data points, otherwise the plot gets "blurry"
        step = max(1, len(times) // max_points)

        # Reduce times with step
        reduced_times = times[::step]

        # Bin values by step (average)
        reduced_values = [
            sum(values[i:i+step]) / len(values[i:i+step])
            for i in range(0, len(values), step)
        ]

        return reduced_times[:len(reduced_values)], reduced_values
    

    def units(self, units):
        self._unit = units


    def update_time_range(self, selected_time):
        if selected_time == -1:
            new_times, new_values = self.reduce_data(self.times(), self.hashrate_data())
            self.replot({"times": new_times, "values": new_values, "units": self.units})
            return

        selected_time = int(selected_time)
        max_length = len(self.hashrate_data())
        if selected_time > max_length:
            selected_time = max_length
        new_values = self.hashrate_data()[-selected_time:]
        new_times = self.times()[-selected_time:]
        new_times, new_values = self.reduce_data(new_times, new_values)
        self.replot({"times": new_times, "values": new_values})


    def replot(self, data: dict[str, Any]) -> None:
        """Update the data for the weather plot.

        Args:
            data: Hashrate data.
            values: The name of the values to plot.
        """
        self.plt.clear_data()
        self._data = data["values"]
        self._time = data["times"]
        self.plot()

