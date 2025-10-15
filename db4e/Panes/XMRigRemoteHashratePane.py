"""
db4e/Panes/XMRigRemoteHashratePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Label, Select

from db4e.Modules.XMRigRemote import XMRigRemote
from db4e.Widgets.Db4EPlot import Db4EPlot

from db4e.Modules.Helper import minutes_to_uptime

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DForm import DForm
from db4e.Constants.DSelect import DSelect



class XMRigRemoteHashratePane(Container):

    selected_time = DSelect.ONE_WEEK
    intro_label = Label("", classes=DForm.INTRO)
    hashrate_plot = Db4EPlot(
        DLabel.HASHRATE, id=DField.HASHRATE_PLOT, classes=DField.HASHRATE_PLOT)
    select_widget = Select(compact=True, id=DForm.TIMES, options=DSelect.HOURS_SELECT_LIST)

    def compose(self):
        # Remote P2Pool daemon deployment form
        yield Vertical(
            ScrollableContainer(
                self.intro_label,

                Vertical(
                    self.select_widget,
                    classes=DForm.SELECT_BOX),

                Vertical(
                    self.hashrate_plot,
                    classes=DForm.PANE_BOX)),

                classes=DForm.PANE_BOX)


    def on_select_changed(self, event: Select.Changed) -> None:
        selected_time = event.value
        self.hashrate_plot.update_time_range(selected_time)


    def set_data(self, xmrig: XMRigRemote):
        self.xmrig = xmrig
        INTRO = f"Hashrate for the [cyan]{DLabel.XMRIG_REMOTE}[/] " \
            f"([cyan]{xmrig.instance()})[/] deployment."
        self.intro_label.update(INTRO)

        data = xmrig.hashrates()
        if type(data) == dict:
            days = data[DField.DAYS]
            hashrates = data[DField.VALUES]
            units = data[DField.UNITS]
            plot = self.query_one("#" + DField.HASHRATE_PLOT, Db4EPlot)
            plot.load_data(days=days, values=hashrates, units=units)
            plot.db4e_plot()


