"""
db4e/App.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

"""


import os
import time
from dataclasses import dataclass, field, fields
from importlib import metadata
from textual.app import App
from textual.containers import Vertical
from textual import work
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
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.MessageRouter import MessageRouter
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.UpdateTopBar import UpdateTopBar
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Fields import (
    COLORTERM_ENVIRON_FIELD, TERM_ENVIRON_FIELD, TO_METHOD_FIELD,
    TO_MODULE_FIELD)
from db4e.Constants.Defaults import (
    APP_TITLE_DEFAULT, COLORTERM_DEFAULT, CSS_PATH_DEFAULT, TERM_DEFAULT)

class Db4EApp(App):
    TITLE = APP_TITLE_DEFAULT
    CSS_PATH = CSS_PATH_DEFAULT
    REFRESH_TIME = 2

    def __init__(self):
        super().__init__()
        self.ops_mgr = OpsMgr()
        self.pane_mgr = PaneMgr(catalogue=PaneCatalogue())
        self.nav_pane = NavPane(ops_mgr=self.ops_mgr)
        self.msg_router = MessageRouter()


    def compose(self):
        self.topbar = TopBar(app_version=__version__)
        yield self.topbar
        yield Vertical(
            self.nav_pane,
            Clock()
        )
        yield self.pane_mgr


    ### Message handling happens here...#31b8e6;

    # Exit the app
    def on_quit(self) -> None:
        self.exit()
    
    # Every form sends the form data here
    @work(exclusive=True)
    async def on_db4e_msg(self, message: Db4eMsg) -> None:
        print(f"Db4EApp:on_db4e_msg(): form_data: {message.form_data}")
        data, pane = self.msg_router.dispatch(
            message.form_data[TO_MODULE_FIELD],
            message.form_data[TO_METHOD_FIELD],
            message.form_data
        )
        self.pane_mgr.set_pane(name=pane, data=data)


    # Handle requests to refresh the NavPane
    @work(exclusive=True)
    async def on_refresh_nav_pane(self, message: RefreshNavPane) -> None:
        #self.ops_mgr.depl_mgr.db_cache.refresh()
        self.nav_pane.refresh_nav_pane()


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

    app = Db4EApp()
    app.run()

if __name__ == "__main__":
    main()