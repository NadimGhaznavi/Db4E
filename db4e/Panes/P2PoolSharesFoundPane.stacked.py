"""
db4e/Panes/P2PoolSharesFoundPane.py

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

from db4e.Widgets.Db4EPlot import HashratePlot

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DForm import DForm
from db4e.Constants.DSelect import DSelect




class P2PoolSharesFoundPane(Container):

    intro_label = Label("", classes=DForm.INTRO)
    instance_label = Label("", id=DForm.INSTANCE_LABEL,classes=DForm.STATIC)
    days = reactive([])


    def compose(self):

        yield Vertical(
            ScrollableContainer(
                self.intro_label,

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_15),
                        self.instance_label),
                    classes=DForm.FORM_1),                 

                Vertical(
                    PlotextPlot(),
                    classes=DForm.PANE_BOX)),

                classes=DForm.PANE_BOX)

    def on_mount(self) -> None:
        plt = self.query_one(PlotextPlot).plt
        plt.bar([], [], color="blue")
        plt.title("Blocks Found")

    
    def reduce_data(self, days, miner_lists, max_bars=20):
        n = len(days)
        if n <= max_bars:
            return days, miner_lists  # nothing to do

        bin_size = math.ceil(n / max_bars)
        agg_days = []
        new_miner_lists = []
        new_miner_lists = [[] for _ in miner_lists]

        for i in range(0, n, bin_size):
            bin_days = days[i:i + bin_size]
            for idx, miner_list in enumerate(miner_lists):
                new_miner_lists[idx].append(sum(miner_list[i:i + bin_size]))


            # Average or sum — depending on your preference
            agg_days.append(int(sum(bin_days) // len(bin_days)))  # midpoint of the bin

        print(f"P2PoolSharesFoundPane:reduce_data(): agg_days: {agg_days}")
        for miner_list in new_miner_lists:
            print(f"P2PoolSharesFoundPane:reduce_data(): miner_list: {miner_list}")
        return agg_days, new_miner_lists


    def set_data(self, p2pool: P2Pool):
        print(f"P2PoolSharesFoundPane:set_data(): {p2pool.shares_found()}")
        INTRO = f"View historical [i]Shares Found[/] data for the " \
            f"[cyan]{p2pool.instance()} {DLabel.P2POOL_SHORT}[/] deployment."

        self.intro_label.update(INTRO)
        self.instance_label.update(p2pool.instance())

        data = p2pool.shares_found()
        plt = self.query_one(PlotextPlot).plt
        plt.xlabel(DLabel.DAYS)
        plt.ylabel(DLabel.SHARES_FOUND)
        plt.clear_data()
        print(f"P2PoolSharesFoundPane:set_data(): data: {data}")
        if type(data) == dict:
            days = data[DField.DAYS]
            shares_found = data[DField.VALUES]
            miners = data[DField.MINERS]
            days, shares_found = self.reduce_data(days, shares_found)
            plt.stacked_bar(days, shares_found, labels=miners)
            plt.title("Shares Found")


    def watch_days(self, old, new):
        return
        print(f"P2PoolSharesFoundPane:watch_days(): new: {new}")
        plt = self.query_one(PlotextPlot).plt

        plt.bar(self.days, self.shares_found, color="blue")
        plt.title("Shares Found")

