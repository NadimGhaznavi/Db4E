"""
db4e/Modules/PaneMgr.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""
import inspect
from dataclasses import dataclass, field
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import ContentSwitcher
from textual.reactive import reactive

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.PaneCatalogue import PaneCatalogue
from db4e.Modules.Helper import get_effective_identity
from db4e.Messages.UpdateTopBar import UpdateTopBar
from db4e.Constants.Panes import INITIAL_SETUP_PANE, WELCOME_PANE, RESULTS_PANE

@dataclass
class PaneState:
    name: str = ""
    data: dict = field(default_factory=dict)

class PaneMgr(Widget):
    pane_state = reactive(PaneState(), always_update=True)

    def __init__(self, config: Config, catalogue: PaneCatalogue, initialized_flag: bool):
        super().__init__()
        self.config = config
        self.catalogue = catalogue
        self._initialized = initialized_flag
        self.panes = {}

    def compose(self):
        with ContentSwitcher(initial=self.pane_state.name, id="content_switcher"):
            for pane_name in self.catalogue.registry:
                # Instantiate each pane once, store a reference
                pane = self.catalogue.get_pane(pane_name)
                self.panes[pane_name] = pane
                yield pane

    def on_mount(self) -> None:
        initial = PaneState(name=WELCOME_PANE if self._initialized else INITIAL_SETUP_PANE, data={})
        if initial.name == INITIAL_SETUP_PANE:
            initial.data = get_effective_identity()
        self.set_pane(initial.name, initial.data)

    def set_initialized(self, value: bool) -> None:
        self._initialized = value

    def set_pane(self, name: str, data: dict | None = None):
        #print(f"PaneMgr:set_pane(): {name}/{data}")
        if not self._initialized and name != RESULTS_PANE:
            self.pane_state = PaneState(INITIAL_SETUP_PANE, data)
        elif name == RESULTS_PANE and not data:
            self.pane_state = PaneState(WELCOME_PANE, {})
        else:
            self.pane_state = PaneState(name, data)
        # If the pane supports set_data, update it with new data
        if data and name in self.panes:
            pane = self.panes[name]
            if hasattr(pane, "set_data"):
                pane.set_data(data)

    def watch_pane_state(self, old: PaneState, new: PaneState):
        try:
            content_switcher = self.query_one("#content_switcher", ContentSwitcher)
        except NoMatches:
            return
        content_switcher.current = new.name
        # Create a message to update the TopBar's title and sub_title
        title, sub_title = self.catalogue.get_metadata(new.name)
        self.post_message(UpdateTopBar(self, title=title, sub_title=sub_title))

