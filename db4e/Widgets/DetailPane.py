# db4e/Widgets/DetailPane.py

from textual.widgets import Static

class DetailPane(Static):
    def __init__(self, **kwargs):
        super().__init__("DetailPane placeholder", **kwargs)