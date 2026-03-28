# db4e/Panes/XMRigHashratesPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label, Select

from db4e.recs.monero.XMRig import XMRig
from db4e.widgets.HashratePlot import HashratePlot
from db4e.util.Helper import minutes_to_uptime

from db4e.constants.DForm import DForm
from db4e.constants.DField import DField
from db4e.constants.DLabel import DLabel
from db4e.constants.DSelect import DSelect


class XMRigHashratesPane(Container):
    """Textual pane for XMRigHashratesPane."""


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
                    Horizontal(
                        Label(DLabel.UPTIME, classes=DForm.FORM_LABEL_15),
                        Label("", id=DForm.UPTIME_LABEL, classes=DForm.STATIC),
                    ),
                    classes=DForm.FORM_3,
                    id=DForm.FORM_FIELD,
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
                    HashratePlot(id=DField.HASHRATE_PLOT, classes=DField.HASHRATE_PLOT),
                    classes=DForm.PANE_BOX,
                ),
                classes=DForm.PANE_BOX,
            )
        )

    def on_mount(self):
        """Handle the mount lifecycle event.
        
        :return: None
        :rtype: None
        """
        self.query_one(Select).value = DSelect.ONE_WEEK_HOURS
        self.query_one(f"#{DField.HASHRATE_PLOT}", HashratePlot).hashrate_plot(
            DSelect.ONE_WEEK
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changed events.
        
        :param event: Event payload.
        :type event: Select.Changed
        :return: None
        :rtype: None
        """
        selected_time = event.value
        self.query_one(f"#{DField.HASHRATE_PLOT}", HashratePlot).hashrate_plot(
            selected_time
        )

    def set_data(self, xmrig: XMRig):
        """Set the data for the pane.
        
        :param xmrig: XMRig deployment object.
        :type xmrig: XMRig
        :return: None
        :rtype: None
        """
        # Update textual labels
        self.query_one(f"#{DForm.INTRO}", Label).update(
            f"View historical hashrate data for the [cyan]{xmrig.instance()} {DLabel.XMRIG}[/] deployment."
        )
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(xmrig.instance())
        self.query_one(f"#{DForm.HASHRATE_LABEL}", Label).update(str(xmrig.hashrate()))
        self.query_one(f"#{DForm.UPTIME_LABEL}", Label).update(
            minutes_to_uptime(xmrig.uptime())
        )

        # Load and plot hashrate data
        data = xmrig.hashrates()
        if isinstance(data, dict):
            plot = self.query_one(f"#{DField.HASHRATE_PLOT}", HashratePlot)
            plot.load_data(days=data[DField.DAYS], values=data[DField.VALUES])
            plot.hashrate_plot(DSelect.ONE_WEEK_HOURS)
