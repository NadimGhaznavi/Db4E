"""
db4e/Panes/PaymentsPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label, Select

from db4e.Widgets.Db4EPlot import Db4EPlot

from db4e.Constants.DForm import DForm
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DSelect import DSelect



class PaymentsPane(Container):

    selected_time = DSelect.ONE_WEEK
    payment_plot = Db4EPlot(DLabel.PAYMENTS, id=DField.DB4E_PLOT)
    select_widget = Select(compact=True, id=DForm.TIMES, options=DSelect.HOURS_SELECT_LIST)


    def compose(self):

        INTRO = f"XMR payment history."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    self.select_widget,
                    classes=DForm.SELECT_BOX),

                Vertical(
                    self.payment_plot,
                    classes=DForm.PANE_BOX)),

                classes=DForm.PANE_BOX)


    def on_select_changed(self, event: Select.Changed) -> None:
        selected_time = event.value
        self.payment_plot.update_time_range(selected_time)


    def set_data(self, payment_data: dict):
        if type(payment_data) == dict:
            days = payment_data[DField.DAYS]
            payments = payment_data[DField.VALUES]
            units = "XMR"
            
            plot = self.query_one("#" + DField.DB4E_PLOT, Db4EPlot)
            plot.load_data(days=days, values=payments, units=units)
            plot.db4e_plot()  