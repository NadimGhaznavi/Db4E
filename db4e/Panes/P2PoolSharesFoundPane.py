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

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DForm import DForm



class P2PoolSharesFoundPane(Container):

    intro_label = Label("", classes=DForm.INTRO)
    instance_label = Label("", id=DForm.INSTANCE_LABEL,classes=DForm.STATIC)
    days = reactive([])
    shares_found = reactive([])


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
        plt.bar(self.days, self.shares_found, color="blue")
        plt.title("Shares Found")

    
    def reduce_data(self, days, shares_found, max_bars=100):
        n = len(days)
        if n <= max_bars:
            return days, shares_found  # nothing to do

        bin_size = math.ceil(n / max_bars)
        agg_days = []
        agg_shares = []

        for i in range(0, n, bin_size):
            bin_days = days[i:i + bin_size]
            bin_shares = shares_found[i:i + bin_size]
            # Average or sum — depending on your preference
            agg_days.append(int(sum(bin_days) / len(bin_days)))  # midpoint of the bin
            agg_shares.append(sum(bin_shares))  # total for that bin

        return agg_days, agg_shares


    def set_data(self, p2pool: P2Pool):
        print(f"P2PoolSharesFoundPane:set_data()")
        INTRO = f"View historical [i]Shares Found[/] data for the " \
            f"[cyan]{p2pool.instance()}[/] deployment."
        
        self.intro_label.update(INTRO)
        self.instance_label.update(p2pool.instance())

        data = p2pool.shares_found()
        plt = self.query_one(PlotextPlot).plt
        plt.xlabel(DLabel.DAYS)
        plt.ylabel(DLabel.BLOCKS_FOUND)
        plt.clear_data()
        print(f"P2PoolSharesFoundPane:set_data(): data: {data}")
        if type(data) == dict:
            self.days = data[DField.DAYS]
            self.shares_found = data[DField.VALUES]
            self.days, self.shares_found = self.reduce_data(self.days, self.shares_found)
            plt.bar(self.days, self.shares_found, color="blue")
            plt.title("Shares Found")


    def watch_days(self, old, new):
        print(f"P2PoolSharesFoundPane:watch_days(): new: {new}")
        plt = self.query_one(PlotextPlot).plt

        plt.bar(self.days, self.shares_found, color="blue")
        plt.title("Shares Found")

