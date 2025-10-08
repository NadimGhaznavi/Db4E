"""
db4e/Panes/P2PoolAnalyticsPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, ScrollableContainer, Horizontal
from textual.widgets import Label, Select


from db4e.Modules.P2Pool import P2Pool
from db4e.Widgets.Db4EPlot import Db4EPlot

from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DForm import DForm
from db4e.Constants.DSelect import DSelect



class P2PoolSharesFoundPane(Container):

    selected_time = DSelect.ONE_WEEK
    intro_label = Label("", classes=DForm.INTRO)
    instance_label = Label("", id=DForm.INSTANCE_LABEL,classes=DForm.STATIC)
    shares_found_label = Label("", id=DForm.HASHRATE_LABEL, classes=DForm.STATIC)
    shares_found_plot = Db4EPlot(DLabel.SHARES_FOUND, id=DField.DB4E_PLOT)
    select_widget = Select(compact=True, id=DForm.TIMES, options=DSelect.SELECT_LIST)


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
                    self.select_widget,
                    classes=DForm.SELECT_BOX),

                Vertical(
                    self.shares_found_plot,
                    classes=DForm.PANE_BOX)),

                classes=DForm.PANE_BOX)

    
    def on_select_changed(self, event: Select.Changed) -> None:
        selected_time = event.value
        self.shares_found_plot.update_time_range(selected_time)


    def set_data(self, p2pool: P2Pool):
        INTRO = f"The chart below shows the shares found for the " \
            f"[cyan]{p2pool.instance()} {DLabel.P2POOL}[/] deployment. This is the " \
            f"cumulative total of the individual miners connected to this P2Pool " \
            f"instance."
        
        self.intro_label.update(INTRO)
        self.instance_label.update(p2pool.instance())

        data = p2pool.shares_found()
        if type(data) == dict:
            days = data[DField.DAYS]
            shares_found = data[DField.VALUES]
            
            plot = self.query_one("#" + DField.DB4E_PLOT, Db4EPlot)
            plot.load_data(days=days, values=shares_found, units="")
            plot.db4e_plot()        

