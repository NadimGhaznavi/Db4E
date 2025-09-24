"""
db4e/Panes/XMRigRemotePane.py

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

from db4e.Widgets.HashratePlot import HashratePlot

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DForm import DForm
from db4e.Constants.DSelect import DSelect



class XMRigRemotePane(Container):

    selected_time = DSelect.ONE_WEEK
    instance_label = Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC)
    ip_addr_label = Label("", id=DForm.IP_ADDR_LABEL, classes=DForm.STATIC)
    hashrate_label = Label("", id=DForm.HASHRATE_LABEL, classes=DForm.STATIC)
    uptime_label = Label("", id=DForm.UPTIME_LABEL, classes=DForm.STATIC)
    hashrate_plot = HashratePlot(DLabel.HASHRATE, id=DField.HASHRATE_PLOT)
    xmrig_remote = None


    def compose(self):
        # Remote P2Pool daemon deployment form
        INTRO = f"View information about the [cyan]{DLabel.XMRIG_REMOTE}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_20),
                        self.instance_label),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=DForm.FORM_LABEL_20),
                        self.ip_addr_label),
                    Horizontal(
                        Label(DLabel.HASHRATE, classes=DForm.FORM_LABEL_20),
                        self.hashrate_label),
                    Horizontal(
                        Label(DLabel.UPTIME, classes=DForm.FORM_LABEL_20),
                        self.uptime_label),
                    classes=DForm.FORM_4, id=DForm.FORM_FIELD),

                Vertical(
                    Select(compact=True, id=DForm.TIMES, options=DSelect.SELECT_LIST),
                    self.hashrate_plot,
                    classes=DForm.PANE_BOX)),
                classes=DForm.PANE_BOX)
        
    def on_select_changed(self, event: Select.Changed) -> None:
        selected_time = event.value
        hashrate_widget = self.query_one("#" + DField.HASHRATE_PLOT)
        hashrate_widget.update_time_range(selected_time)


    def set_data(self, xmrig: XMRigRemote):
        #print(f"XMRig:set_data(): {xmrig}")
        self.xmrig = xmrig
        self.instance_label.update(xmrig.instance())
        self.ip_addr_label.update(xmrig.ip_addr())
        self.hashrate_label.update(str(xmrig.hashrate()) + " " + DLabel.H_PER_S)
        self.uptime_label.update(xmrig.uptime())

        hashrate_widget = self.query_one("#" + DField.HASHRATE_PLOT)
        hashrate_widget.load_all_data(xmrig.hashrates())
        hashrate_widget.update_time_range(self.selected_time)

        select_widget = self.query_one("#" + DForm.TIMES)
        select_widget.value = self.selected_time