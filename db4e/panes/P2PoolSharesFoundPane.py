# db4e/Panes/P2PoolSharesFoundPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label, Select


from db4e.recs.monero.P2Pool import P2Pool
from db4e.widgets.SharesFoundPlot import SharesFoundPlot

from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DForm import DForm
from db4e.constants.DSelect import DSelect


class P2PoolSharesFoundPane(Container):
    """Textual pane for P2PoolSharesFoundPane."""


    selected_time = DSelect.ONE_WEEK
    shares_found_label = Label("", id=DForm.HASHRATE_LABEL, classes=DForm.STATIC)

    def compose(self):
        """Compose the pane layout.
        
        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """

        yield Vertical(
            ScrollableContainer(
                Label("", id=DForm.INTRO, classes=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_15),
                        Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC),
                    ),
                    classes=DForm.FORM_1,
                ),
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

    def set_data(self, p2pool: P2Pool):
        """Set the data for the pane.
        
        :param p2pool: P2Pool deployment object.
        :type p2pool: P2Pool
        :return: None
        :rtype: None
        """
        INTRO = (
            f"The chart below shows the shares found for the "
            f"[cyan]{p2pool.instance()} {DLabel.P2POOL}[/] deployment. This is the "
            f"cumulative total of the individual miners connected to this P2Pool "
            f"instance."
        )

        self.query_one(f"#{DForm.INTRO}", Label).update(INTRO)
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(p2pool.instance())

        data = p2pool.shares_found()
        if type(data) == dict:
            days = data[DField.DAYS]
            shares_found = data[DField.VALUES]
            plot = self.query_one(SharesFoundPlot)
            plot.load_data(days=days, values=shares_found)
            plot.found_shares_plot(DSelect.ONE_WEEK)
