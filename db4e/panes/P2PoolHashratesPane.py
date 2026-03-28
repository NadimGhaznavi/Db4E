# db4e/Panes/P2PoolHashratesPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label, Select

from db4e.recs.monero.P2Pool import P2Pool
from db4e.widgets.Db4EPlot import Db4EPlot

from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DForm import DForm
from db4e.constants.DSelect import DSelect


class P2PoolHashratesPane(Container):
    """Textual pane for P2PoolHashratesPane."""


    selected_time = DSelect.ONE_WEEK_HOURS

    def compose(self):
        """Compose the pane layout.
        
        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_15),
                        Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.HASHRATE, classes=DForm.FORM_LABEL_15),
                        Label("", id=DForm.HASHRATE_LABEL, classes=DForm.STATIC),
                    ),
                    classes=DForm.FORM_2,
                ),
                Vertical(
                    Select(
                        compact=True,
                        id=DForm.TIMES,
                        allow_blank=False,
                        options=DSelect.HOURS_SELECT_LIST,
                    ),
                    classes=DForm.SELECT_BOX,
                ),
                Vertical(
                    Db4EPlot(DLabel.HASHRATE, id=DField.HASHRATE_PLOT),
                    classes=DForm.PANE_BOX,
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changed events.
        
        :param event: Event payload.
        :type event: Select.Changed
        :return: None
        :rtype: None
        """
        self.selected_time = event.value
        plot = self.query_one(f"#{DField.HASHRATE_PLOT}", Db4EPlot)
        plot.update_time_range(self.selected_time)

    def set_data(self, p2pool: P2Pool):
        """Set the data for the pane.
        
        :param p2pool: P2Pool deployment object.
        :type p2pool: P2Pool
        :return: None
        :rtype: None
        """
        intro_text = (
            f"The chart below shows the hashrate for the "
            f"[cyan]{p2pool.instance()} {DLabel.P2POOL}[/] deployment. "
            "This is the cumulative total of the individual miners connected "
            "to this P2Pool deployment."
        )
        self.query_one(f"#{DForm.INTRO}", Label).update(intro_text)
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(p2pool.instance())
        self.query_one(f"#{DForm.HASHRATE_LABEL}", Label).update(str(p2pool.hashrate()))

        data = p2pool.hashrates()
        if isinstance(data, dict):
            days = data[DField.DAYS]
            hashrates = data[DField.VALUES]
            units = data[DField.UNITS]

            plot = self.query_one(f"#{DField.HASHRATE_PLOT}", Db4EPlot)
            plot.load_data(days=days, values=hashrates, units=units)
            plot.db4e_plot()
