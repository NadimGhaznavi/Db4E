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
from db4e.Modules.Db4eService import Db4eService
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.InstallMgr import InstallMgr
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.MessageRouter import MessageRouter
from db4e.Messages.SubmitFormData import SubmitFormData
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
            self.install_mgr = InstallMgr(config=config)
            self.pane_catalogue = PaneCatalogue()
            self.msg_router = MessageRouter(config=config)
            self.depl_mgr = DeploymentMgr(config=config)
            self._initialized = False
            initialized_flag = self.depl_mgr.is_initialized()
            self.pane_mgr = PaneMgr(
                config=config, catalogue=self.pane_catalogue, 
                initialized_flag=initialized_flag)
            self.nav_pane = NavPane(config=config, ops_mgr=self.ops_mgr)
            self.set_initialized()
        elif op == RUN_SERVICE_FIELD:
            self.ops_mgr = OpsMgr(config=config)
            initialized_flag = self.depl_mgr.is_initialized()
            self.pane_catalogue = PaneCatalogue()
            self.msg_router = MessageRouter(config=config)
            self.pane_mgr = PaneMgr(
                config=config, catalogue=self.pane_catalogue, 
                initialized_flag=initialized_flag)
            self.nav_pane = NavPane(config=config, ops_mgr=self.ops_mgr)
            self.service = Db4eService(config=config)
            self.service.start()
        
    def compose(self):
        self.topbar = TopBar(app_version=__version__)
        yield self.topbar
        yield Vertical(
            self.nav_pane,
            Clock()
        )
        yield self.pane_mgr

    def is_initialized(self) -> bool:
        #print(f"App:is_initialized(): {self._initialized}")
        return self._initialized

    ### Message handling happens here...

    # NavPane selections are routed here
    def on_nav_leaf_selected(self, message: NavLeafSelected) -> None:
        route = f"nav:select:{message.parent}:{message.leaf}"
        name, data = self.msg_router.dispatch(route)
        self.pane_mgr.set_pane(name=name, data=data)

    # Exit the app
    def on_quit(self) -> None:
        self.exit()
    
    # Every form sends the form data here
    def on_submit_form_data(self, message: SubmitFormData) -> None:
        data, pane = self.msg_router.dispatch(
            message.form_data[TO_MODULE_FIELD],
            message.form_data[TO_METHOD_FIELD],
            message.form_data
        )
        if not self.is_initialized():
            self.set_initialized()
        self.pane_mgr.set_pane(name=pane, data=data)
        self.nav_pane.refresh_nav_pane()


    # Handle requests to refresh the NavPane
    def on_refresh_nav_pane(self, message: RefreshNavPane) -> None:
        self.nav_pane.flush_cache()

    # The individual Detail panes use this to update the TopBar
    def on_update_top_bar(self, message: UpdateTopBar) -> None:
        self.topbar.set_state(title=message.title, sub_title=message.sub_title )

    def set_initialized(self) -> None:
        flag = self.depl_mgr.is_initialized()
        self.pane_mgr.set_initialized(flag)
        self.nav_pane.check_initialized()
        self._initialized = flag
        #print(f"App:set_initialized(): initialized: {flag}")

    # Catchall 
    def _handle_exception(self, error: Exception) -> None:
        self.bell()
        self.exit(message=Traceback(show_locals=True, width=None, locals_max_length=5))

def main():
    # Set environment variables for better color support
    os.environ[TERM_ENVIRON_FIELD] = TERM_DEFAULT
    os.environ[COLORTERM_ENVIRON_FIELD] = COLORTERM_DEFAULT

    config_manager = ConfigMgr(__version__)
    config = config_manager.get_config()
    app = Db4EApp(config)
    app.run()

if __name__ == "__main__":
    main()