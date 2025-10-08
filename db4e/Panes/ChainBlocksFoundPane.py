"""
db4e/Panes/ChainBlocksFoundPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
import math

from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label, Select
from textual_plotext import PlotextPlot
from textual.reactive import reactive

from db4e.Modules.P2Pool import P2Pool

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DForm import DForm
from db4e.Constants.DSelect import DSelect




class ChainBlocksFoundPane(Container):

    intro_label = Label("", classes=DForm.INTRO)
    days = reactive([])
    blocks_found = reactive([])


    def compose(self):

        yield Vertical(
            ScrollableContainer(
                self.intro_label,

                Vertical(
                    PlotextPlot(),
                    classes=DForm.PANE_BOX)),

                classes=DForm.PANE_BOX)

    def on_mount(self) -> None:
        plt = self.query_one(PlotextPlot).plt
        plt.bar(self.days, self.blocks_found, color="blue")
        plt.title("Blocks Found")

    
    def reduce_data(self, days, blocks_found, max_bars=100):
        n = len(days)
        if n <= max_bars:
            return days, blocks_found  # nothing to do

        bin_size = math.ceil(n / max_bars)
        agg_days = []
        agg_blocks = []

        for i in range(0, n, bin_size):
            bin_days = days[i:i + bin_size]
            bin_blocks = blocks_found[i:i + bin_size]
            # Average or sum — depending on your preference
            agg_days.append(int(sum(bin_days) / len(bin_days)))  # midpoint of the bin
            agg_blocks.append(sum(bin_blocks))  # total for that bin

        return agg_days, agg_blocks


    def set_data(self, p2pool: P2Pool):
        print(f"ChainBlocksFoundPane:set_data()")
        LONG_NAME = {
            DLabel.MINI_CHAIN: "Mini Sidechain",
            DLabel.MAIN_CHAIN: "Mainchain",
            DLabel.NANO_CHAIN: "Nano Sidechain"
        }
        INTRO = f"View historical [i]Blocks Found[/] data for the " \
            f"[cyan]{LONG_NAME[p2pool.instance()]}."
        
        self.intro_label.update(INTRO)

        data = p2pool.blocks_found()
        plt = self.query_one(PlotextPlot).plt
        plt.xlabel(DLabel.DAYS)
        plt.ylabel(DLabel.BLOCKS_FOUND)
        plt.clear_data()
        print(f"ChainBlocksFoundPane:set_data(): data: {data}")
        if type(data) == dict:
            self.days = data[DField.DAYS]
            self.blocks_found = data[DField.VALUES]
            self.days, self.blocks_found = self.reduce_data(self.days, self.blocks_found)
            plt.bar(self.days, self.blocks_found, color="blue")
            plt.title("Blocks Found")


    def watch_days(self, old, new):
        print(f"ChainBlocksFoundPane:watch_days(): new: {new}")
        plt = self.query_one(PlotextPlot).plt

        plt.bar(self.days, self.blocks_found, color="blue")
        plt.title("Blocks Found")

