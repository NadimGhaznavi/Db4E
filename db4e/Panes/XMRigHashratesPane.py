"""
db4e/Panes/XMRigAnalyticsPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label, Select

from db4e.Modules.XMRig import XMRig

from db4e.Widgets.Db4EPlot import Db4EPlot

from db4e.Modules.Helper import minutes_to_uptime


from db4e.Constants.DForm import DForm
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DSelect import DSelect



class XMRigHashratesPane(Container):

    selected_time = DSelect.ONE_WEEK
    intro_label = Label("", classes=DForm.INTRO)
    instance_label = Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC)
    hashrate_label = Label("", id=DForm.HASHRATE_LABEL, classes=DForm.STATIC)
    uptime_label = Label("", id=DForm.UPTIME_LABEL, classes=DForm.STATIC)
    hashrate_plot = Db4EPlot(DLabel.HASHRATE, id=DField.HASHRATE_PLOT)
    select_widget = Select(compact=True, id=DForm.TIMES, options=DSelect.HOURS_SELECT_LIST)


    def compose(self):

        yield Vertical(
            ScrollableContainer(
                self.intro_label,

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_15),
                        self.instance_label),
                    Horizontal(
                        Label(DLabel.HASHRATE, classes=DForm.FORM_LABEL_15),
                        self.hashrate_label),
                    Horizontal(
                        Label(DLabel.UPTIME, classes=DForm.FORM_LABEL_15),
                        self.uptime_label),
                    classes=DForm.FORM_3, id=DForm.FORM_FIELD),

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


    def set_data(self, xmrig: XMRig):
        INTRO = f"View historical hashrate data for the [cyan]{xmrig.instance()} " \
            f"{DLabel.XMRIG}[/] deployment."
        self.intro_label.update(INTRO)
        self.instance_label.update(xmrig.instance())
        self.hashrate_label.update(str(xmrig.hashrate()))
        self.uptime_label.update(minutes_to_uptime(xmrig.uptime()))

        data = xmrig.hashrates()
        if type(data) == dict:
            days = data[DField.DAYS]
            hashrates = data[DField.VALUES]
            units = data[DField.UNITS]
            
            plot = self.query_one("#" + DField.HASHRATE_PLOT, Db4EPlot)
            plot.load_data(days=days, values=hashrates, units=units)
            plot.db4e_plot()  