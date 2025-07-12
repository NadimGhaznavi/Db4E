"""
db4e/App.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""


import os
import sys
from dataclasses import dataclass, field, fields
from importlib import metadata
from textual.app import App
from textual.theme import Theme as TextualTheme
from textual.widgets import Footer
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
from db4e.Widgets.DetailPane import DetailPane
from db4e.Widgets.NavPane import NavPane
from db4e.Modules.ConfigMgr import ConfigMgr, Config
from db4e.Modules.DeploymentMgr import DeploymentMgr
from db4e.Modules.PaneCatalogue import PaneCatalogue
from db4e.Modules.PaneMgr import PaneMgr
from db4e.Modules.InstallMgr import InstallMgr
from db4e.Modules.MessageRouter import MessageRouter
from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Messages.UpdateTopBar import UpdateTopBar
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Messages.NavLeafSelected import NavLeafSelected
from db4e.Constants.Fields import (
    COLORTERM_ENVIRON_FIELD, COMPONENT_FIELD, DB4E_FIELD, MONEROD_FIELD, P2POOL_FIELD,
    REMOTE_FIELD, TERM_ENVIRON_FIELD, TO_MODULE_FIELD, 
    TO_METHOD_FIELD
)
from db4e.Constants.Labels import (
    DB4E_LABEL, DEPLOYMENTS_LABEL, MONEROD_SHORT_LABEL, NEW_LABEL, P2POOL_SHORT_LABEL
)
from db4e.Constants.Panes import (
    DB4E_PANE, MONEROD_REMOTE_PANE, NEW_MONEROD_TYPE_PANE, NEW_P2POOL_TYPE_PANE,
    P2POOL_REMOTE_PANE, 
)
from db4e.Constants.Defaults import (
    APP_TITLE_DEFAULT, COLORTERM_DEFAULT, CSS_PATH_DEFAULT, TERM_DEFAULT
)

class Db4EApp(App):
    TITLE = APP_TITLE_DEFAULT
    CSS_PATH = CSS_PATH_DEFAULT

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.depl_mgr = DeploymentMgr(config)
        self.install_mgr = InstallMgr(config)
        self.pane_catalogue = PaneCatalogue()
        self.msg_router = MessageRouter(config)

        initialized_flag = self.depl_mgr.is_initialized()
        self.pane_mgr = PaneMgr(
            config=config, catalogue=self.pane_catalogue, initialized_flag=initialized_flag)
        self.nav_pane = NavPane(config=config)
        self.set_initialized(initialized_flag)
        
    def compose(self):
        self.topbar = TopBar(app_version=__version__)
        yield self.topbar
        yield Vertical(
            self.nav_pane,
            Clock()
        )
        yield self.pane_mgr

    def is_initialized(self) -> bool:
        return self._initialized

    ### Message handling happens here...

    # NavPane selections are routed here
    def on_nav_leaf_selected(self, message: NavLeafSelected) -> None:
        category = message.parent
        instance = message.leaf
        #print(f"App:on_nav_leav_selected(): {category}/{instance}")
        if category == DEPLOYMENTS_LABEL and instance == DB4E_LABEL:
            db4e_data = self.depl_mgr.get_deployment(DB4E_FIELD)
            self.pane_mgr.set_pane(name=DB4E_PANE, data=db4e_data)

        elif category == MONEROD_SHORT_LABEL and instance == NEW_LABEL:
            self.pane_mgr.set_pane(name=NEW_MONEROD_TYPE_PANE)

        elif category == MONEROD_SHORT_LABEL:
            monerod_data = self.depl_mgr.get_deployment_by_instance(
                component=MONEROD_FIELD, instance=instance)
            if monerod_data[REMOTE_FIELD]:
                self.pane_mgr.set_pane(name=MONEROD_REMOTE_PANE, data=monerod_data)

        elif category == P2POOL_SHORT_LABEL and instance == NEW_LABEL:
            self.pane_mgr.set_pane(name=NEW_P2POOL_TYPE_PANE)
        elif category == P2POOL_SHORT_LABEL:
            p2pool_data = self.depl_mgr.get_deployment_by_instance(
                component=P2POOL_FIELD, instance=instance)
            if p2pool_data[REMOTE_FIELD]:
                self.pane_mgr.set_pane(name=P2POOL_REMOTE_PANE, data=p2pool_data)

    # Exit the app
    def on_quit(self) -> None:
        self.exit()
    
    # Every form sends the form data here
    def on_submit_form_data(self, message: SubmitFormData) -> None:
        #print(f"App:on_submit_form_data(): {message.form_data}")
        module = message.form_data[TO_MODULE_FIELD]
        method = message.form_data[TO_METHOD_FIELD]
        results, pane_name = self.msg_router.dispatch(module, method, message.form_data)

        if not self.is_initialized():
            flag = self.depl_mgr.is_initialized()
            self.set_initialized(flag)

        self.pane_mgr.set_pane(name=pane_name, data=results)
        self.nav_pane.refresh_nav_pane()


    # Handle requests to refresh the NavPane
    def on_refresh_nav_pane(self, message: RefreshNavPane) -> None:
        self.nav_pane.refresh_nav_pane()

    # The individual Detail panes use this to update the TopBar
    def on_update_top_bar(self, message: UpdateTopBar) -> None:
        self.topbar.set_state(title=message.title, sub_title=message.sub_title )

    def set_initialized(self, flag: bool) -> None:
        self._initialized = flag
        self.pane_mgr.set_initialized(flag)

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