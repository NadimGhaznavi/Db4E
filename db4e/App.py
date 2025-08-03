"""
db4e/App.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""


import os
import sys
from dataclasses import dataclass, field, fields
from importlib import metadata
from textual.app import App
from textual.theme import Theme as TextualTheme
from textual.widgets import RadioSet, RadioButton
from textual.containers import Vertical
from rich.theme import Theme as RichTheme
from rich.traceback import Traceback

try:
    __package_name__ = metadata.metadata(__package__ or __name__)["Name"]
    __version__ = metadata.version(__package__ or __name__)
except Exception:
    __package_name__ = "Db4E"
    __version__ = "N/A"


from db4e.Widgets.TopBar import TopBar
from db4e.Widgets.Clock import Clock
from db4e.Widgets.NavPane import NavPane
from db4e.Modules.ConfigMgr import ConfigMgr, Config
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.MessageRouter import MessageRouter
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.UpdateTopBar import UpdateTopBar
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Messages.NavLeafSelected import NavLeafSelected
from db4e.Constants.Fields import (
    COLORTERM_ENVIRON_FIELD, DB4E_FIELD,OP_FIELD, RUN_SERVICE_FIELD,
    RUN_UI_FIELD, TERM_ENVIRON_FIELD, TO_METHOD_FIELD,
    TO_MODULE_FIELD)
from db4e.Constants.Defaults import (
    APP_TITLE_DEFAULT, COLORTERM_DEFAULT, CSS_PATH_DEFAULT, TERM_DEFAULT)

class Db4EApp(App):
    TITLE = APP_TITLE_DEFAULT
    CSS_PATH = CSS_PATH_DEFAULT

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.ini = config
        op = self.ini.config[DB4E_FIELD][OP_FIELD]
        if op == RUN_UI_FIELD:
            self.ops_mgr = OpsMgr(config=config)
            self.msg_router = MessageRouter(config=config)
            self.pane_mgr = PaneMgr(
                config=config, catalogue=PaneCatalogue())
            self.nav_pane = NavPane(config=config, ops_mgr=self.ops_mgr)
        elif op == RUN_SERVICE_FIELD:
            pass

    def compose(self):
        self.topbar = TopBar(app_version=__version__)
        yield self.topbar
        yield Vertical(
            self.nav_pane,
            Clock()
        )
        yield self.pane_mgr

    ### Message handling happens here...#31b8e6;
    # NavPane selections are routed here
    def on_nav_leaf_selected(self, message: NavLeafSelected) -> None:
        route = f"nav:select:{message.parent}:{message.leaf}"
        name, data = self.msg_router.dispatch(route)
        self.pane_mgr.set_pane(name=name, data=data)

    # Exit the app
    def on_quit(self) -> None:
        self.exit()
    
    # Every form sends the form data here
    def on_db4e_msg(self, message: Db4eMsg) -> None:
        data, pane = self.msg_router.dispatch(
            message.form_data[TO_MODULE_FIELD],
            message.form_data[TO_METHOD_FIELD],
            message.form_data
        )
        self.pane_mgr.set_pane(name=pane, data=data)
        self.nav_pane.refresh_nav_pane()


    # Handle requests to refresh the NavPane
    def on_refresh_nav_pane(self, message: RefreshNavPane) -> None:
        self.nav_pane.flush_cache()

    # The individual Detail panes use this to update the TopBar
    def on_update_top_bar(self, message: UpdateTopBar) -> None:
        self.topbar.set_state(title=message.title, sub_title=message.sub_title )

    # Catchall 
    def _handle_exception(self, error: Exception) -> None:
        self.bell()
        self.exit(message=Traceback(show_locals=True, width=None, locals_max_length=5))

def main():
    # Set environment variables for better color support
    os.environ[TERM_ENVIRON_FIELD] = TERM_DEFAULT
    os.environ[COLORTERM_ENVIRON_FIELD] = COLORTERM_DEFAULT

    config_mgr = ConfigMgr(__version__)
    config = config_mgr.get_config()
    app = Db4EApp(config)
    app.run()

if __name__ == "__main__":
    main()