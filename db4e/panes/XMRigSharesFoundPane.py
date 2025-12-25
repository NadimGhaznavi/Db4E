# db4e/Panes/XMRigRemoteSharesFoundPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Label, Select

from db4e.recs.monero.XMRigRemote import XMRigRemote
from db4e.widgets.SharesFoundPlot import SharesFoundPlot

from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DForm import DForm
from db4e.constants.DSelect import DSelect


class XMRigSharesFoundPane(Container):
    """Textual pane for XMRigSharesFoundPane."""


    def compose(self):
        """Compose the pane layout.
        
        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        # Remote P2Pool daemon deployment form
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Select(
                        compact=True,
                        id=DForm.TIMES,
                        allow_blank=False,
                        options=DSelect.SELECT_LIST,
                    ),
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
        """Handle the mount lifecycle event.
        
        :return: None
        :rtype: None
        """
        self.query_one(Select).value = DSelect.ONE_WEEK
        self.query_one(SharesFoundPlot).found_shares_plot(DSelect.ONE_WEEK)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changed events.
        
        :param event: Event payload.
        :type event: Select.Changed
        :return: None
        :rtype: None
        """
        selected_time = event.value
        self.query_one(SharesFoundPlot).found_shares_plot(selected_time)

    def set_data(self, xmrig: XMRigRemote):
        """Set the data for the pane.
        
        :param xmrig: XMRig deployment object.
        :type xmrig: XMRigRemote
        :return: None
        :rtype: None
        """
        self.xmrig = xmrig
        INTRO = (
            f"[i]Shares Found[/] for the [cyan]{DLabel.XMRIG}[/] "
            f"([cyan]{xmrig.instance()})[/] deployment."
        )
        self.query_one(f"#{DForm.INTRO}", Label).update(INTRO)

        data = xmrig.shares_found()
        if type(data) == dict:
            plot = self.query_one(SharesFoundPlot)
            plot.load_data(days=data[DField.DAYS], values=data[DField.VALUES])
            plot.found_shares_plot(DSelect.ONE_WEEK)
