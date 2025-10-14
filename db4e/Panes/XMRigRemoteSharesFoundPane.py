"""
db4e/Panes/XMRigRemoteSharesFoundPane.py

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
from db4e.Widgets.SharesFoundPlot import SharesFoundPlot

from db4e.Modules.Helper import minutes_to_uptime

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DForm import DForm
from db4e.Constants.DSelect import DSelect


class XMRigRemoteSharesFoundPane(Container):

    def compose(self):
        # Remote P2Pool daemon deployment form
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Select(compact=True, id=DForm.TIMES, options=DSelect.SELECT_LIST),
                    classes=DForm.SELECT_BOX,
                ),
                Vertical(
                    SharesFoundPlot(
                        id=DForm.SHARES_FOUND_PLOT,
                        classes=DField.HASHRATE_PLOT,
                    ),
                    classes=DForm.PANE_BOX,
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_mount(self):
        self.query_one(Select).value = DSelect.ONE_WEEK
        self.query_one(SharesFoundPlot).found_shares_plot(DSelect.ONE_WEEK)

    def on_select_changed(self, event: Select.Changed) -> None:
        selected_time = event.value
        self.query_one(SharesFoundPlot).found_shares_plot(selected_time)

    def set_data(self, xmrig: XMRigRemote):
        self.xmrig = xmrig
        INTRO = (
            f"[i]Shares Found[/] for the [cyan]{DLabel.XMRIG_REMOTE}[/] "
            f"([cyan]{xmrig.instance()})[/] deployment."
        )
        intro = self.query_one(f"#{DForm.INTRO}", Label)
        intro.update(INTRO)

        data = xmrig.shares_found()
        if type(data) == dict:
            days = data[DField.DAYS]
            shares_found = data[DField.VALUES]
            plot = self.query_one(SharesFoundPlot)
            plot.load_data(days=days, values=shares_found)
            plot.found_shares_plot(DSelect.ONE_WEEK)
