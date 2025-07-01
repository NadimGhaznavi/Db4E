# db4e/Widgets/DetailPane.py

from textual.app import App, ComposeResult
from textual.widgets import ContentSwitcher
from textual.reactive import reactive
from textual.containers import Container

from db4e.Modules.PaneManager import PaneManager


class DetailPane(Container):

    pane_id = reactive('Welcome')

    def __init__(self, container: Container, **kwargs):
        super().__init__(**kwargs)
        self.pane_manager = PaneManager()

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial=self.pane_id):
            cur_pane = self.pane_manager.get_pane(self.pane_id)
            yield cur_pane
