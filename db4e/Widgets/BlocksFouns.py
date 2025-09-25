"""
db4e/Modules/BlocksFound.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from typing import Any

from textual_plotext import PlotextPlot


class BlocksFound(PlotextPlot):
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

    def on_mount(self) -> None:
        """Plot the data using Plotext."""
        self.plt.date_form("Y-m-d H:M")
        self.plt.title(self._title)
        self.plt.xlabel("Time")
        self.plt.ylabel(self._unit)

    def plot(self) -> None:
        """Redraw the plot."""
        self.plt.clear_data()
        self.plt.ylabel(self._unit)
        self.plt.plot(self._time, self._data, marker="braille")
        self.refresh()

    def update(self, data: dict[str, Any]) -> None:
        """Update the data for the weather plot.

        Args:
            data: Hashrate data.
            values: The name of the values to plot.
        """
        self._data = data["values"]
        self._time = data["times"]
        self._unit = data["units"]
        self.plot()

