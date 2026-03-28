# db4e/Panes/ResultsPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from rich import box
from rich.table import Table
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import ScrollableContainer, Vertical

from db4e.messages.RefreshNavPane import RefreshNavPane
from db4e.util.Helper import gen_results_table
from db4e.constants.DForm import DForm


class ResultsPane(Static):
    """Textual pane for ResultsPane."""


    results = Label()

    def __init__(self, **kwargs):
        """Initialize the pane.
        
        :param kwargs: Widget keyword arguments.
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        super().__init__(**kwargs)
        self.results = Static()

    def compose(self):
        """Compose the pane layout.
        
        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        yield Vertical(ScrollableContainer(self.results), classes=DForm.PANE_BOX)

    def set_data(self, elem):
        """Set the data for the pane.
        
        :param elem: Deployment object.
        :type elem: object
        :return: None
        :rtype: None
        """
        msgs = elem.pop_msgs()
        self.results.update(gen_results_table(results=msgs))
        self.post_message(RefreshNavPane(self))
