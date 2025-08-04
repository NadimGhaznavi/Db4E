"""
db4e/Modules/PaneMgr.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
import inspect
from dataclasses import dataclass, field
from copy import deepcopy
from textual.css.query import NoMatches
from textual.widget import Widget
from textual.widgets import ContentSwitcher
from textual.reactive import reactive

from db4e.Modules.ConfigMgr import Config
from db4e.Modules.PaneCatalogue import PaneCatalogue
from db4e.Modules.Helper import get_effective_identity
from db4e.Messages.UpdateTopBar import UpdateTopBar
from db4e.Constants.Panes import (WELCOME_PANE)
from db4e.Constants.Fields import SET_DATA_FIELD, RESET_DATA_FIELD

@dataclass
class PaneState:
    name: str = ""
    data: dict = field(default_factory=dict)

class PaneMgr(Widget):
    pane_state = reactive(PaneState(), always_update=True)

    def __init__(self, config: Config, catalogue: PaneCatalogue):
        super().__init__()
        self.config = config
        self.catalogue = catalogue
        self.panes = {}

    def compose(self):
        with ContentSwitcher(initial=self.pane_state.name, id="content_switcher"):
            for pane_name in self.catalogue.registry:
                # Instantiate each pane once, store a reference
                pane = self.catalogue.get_pane(pane_name)
                self.panes[pane_name] = pane
                #print(f"PaneMgr:compose(): {pane_name}")
                yield pane

    def on_mount(self) -> None:
        initial = PaneState(name=WELCOME_PANE)
        self.set_pane(initial.name, initial.data)

    def set_pane(self, name: str, data: dict | None = None):
        #print(f"PaneMgr:set_pane(): {name}/{data}")
        self.pane_state = PaneState(name, data)
        # If the pane supports set_data, update it with new data
        if data and name in self.panes:
            pane = self.panes[name]
            if hasattr(pane, SET_DATA_FIELD):
                pane.set_data(data)

    def watch_pane_state(self, old: PaneState, new: PaneState):
        try:
            content_switcher = self.query_one("#content_switcher", ContentSwitcher)
        except NoMatches:
            return
        content_switcher.current = new.name
        #print(f"PaneMgr: {new.name}")
        pane = self.catalogue.get_pane(new.name)
        if hasattr(pane, RESET_DATA_FIELD):
            pane.reset_data()

        title, sub_title = self.catalogue.get_metadata(new.name)
        # Create a message to update the TopBar's title and sub_title
        self.post_message(UpdateTopBar(self, title=title, sub_title=sub_title))

