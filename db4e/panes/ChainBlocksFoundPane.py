# db4e/Panes/ChainBlocksFoundPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


import math

from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label, Select
from textual.reactive import reactive

from db4e.recs.monero.P2Pool import P2Pool

from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DForm import DForm


class ChainBlocksFoundPane(Container):
    """
    Textual pane for displaying blocks-found history for a P2Pool chain.
    """

    days = reactive([])
    blocks_found = reactive([])

    def compose(self):
        """
        Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """

        yield Vertical(
            ScrollableContainer(
                Label("", id=DForm.INTRO, classes=DForm.INTRO),
                Vertical(Label("PLOT PLACEHOLDER"), classes=DForm.PANE_BOX),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_mount(self) -> None:
        """
        Handle the mount lifecycle event.

        :return: None
        :rtype: None
        """
        plt = self.query_one(PlotextPlot).plt
        plt.bar(self.days, self.blocks_found, color="blue")
        plt.title("Blocks Found")

    def reduce_data(self, days, blocks_found, max_bars=100):
        """
        Reduce raw data to a maximum number of bars for plotting.

        :param days: Sequence of day indices or timestamps.
        :type days: list[int] or list[float]
        :param blocks_found: Sequence of blocks found values.
        :type blocks_found: list[int]
        :param max_bars: Maximum number of bars to return.
        :type max_bars: int
        :return: Reduced (days, blocks_found) sequences.
        :rtype: tuple[list[int], list[int]]
        """
        n = len(days)
        if n <= max_bars:
            return days, blocks_found  # nothing to do

        bin_size = math.ceil(n / max_bars)
        agg_days = []
        agg_blocks = []

        for i in range(0, n, bin_size):
            bin_days = days[i : i + bin_size]
            bin_blocks = blocks_found[i : i + bin_size]
            # Average or sum — depending on your preference
            agg_days.append(int(sum(bin_days) / len(bin_days)))  # midpoint of the bin
            agg_blocks.append(sum(bin_blocks))  # total for that bin

        return agg_days, agg_blocks

    def set_data(self, p2pool: P2Pool):
        """
        Set the data for the pane and refresh the plot.

        :param p2pool: P2Pool deployment with blocks-found data.
        :type p2pool: P2Pool
        :return: None
        :rtype: None
        """
        print(f"ChainBlocksFoundPane:set_data()")
        LONG_NAME = {
            DLabel.MINI_CHAIN: "Mini Sidechain",
            DLabel.MAIN_CHAIN: "Mainchain",
            DLabel.NANO_CHAIN: "Nano Sidechain",
        }
        INTRO = (
            f"View historical [i]Blocks Found[/] data for the "
            f"[cyan]{LONG_NAME[p2pool.instance()]}."
        )

        self.query_one(f"#{DForm.INTRO}", Label).update(INTRO)

        data = p2pool.blocks_found()
        print(f"ChainBlocksFoundPane:set_data(): data: {data}")
        if type(data) == dict:
            self.days = data[DField.DAYS]
            self.blocks_found = data[DField.VALUES]
            self.days, self.blocks_found = self.reduce_data(
                self.days, self.blocks_found
            )

    def watch_days(self, old, new):
        """
        React to changes in days and refresh the plot.

        :param old: Previous days value.
        :type old: list[int] or list[float]
        :param new: New days value.
        :type new: list[int] or list[float]
        :return: None
        :rtype: None
        """
        pass
