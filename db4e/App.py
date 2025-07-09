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
from db4e.Messages.SwitchPane import SwitchPane
from db4e.Messages.UpdateTopBar import UpdateTopBar
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Messages.NavLeafSelected import NavLeafSelected
from db4e.Constants.Fields import (
    COLORTERM_ENVIRON_FIELD, DB4E_FIELD, TERM_ENVIRON_FIELD, 
    TO_MODULE_FIELD, TO_METHOD_FIELD
)
from db4e.Constants.Labels import DB4E_LABEL, DEPLOYMENTS_LABEL
from db4e.Constants.Panes import DB4E_PANE
from db4e.Constants.Defaults import (
    APP_TITLE_DEFAULT, COLORTERM_DEFAULT, CSS_PATH_DEFAULT, TERM_DEFAULT
)

RICH_THEME =RichTheme(
    {
        "white": "#e9e9e9",
        "green": "#54efae",
        "yellow": "#f6ff8f",
        "dark_yellow": "#e6d733",
        "red": "#fd8383",
        "purple": "#b565f3",
        "dark_gray": "#969aad",
        "b dark_gray": "b #969aad",
        "highlight": "#91abec",
        "label": "#c5c7d2",
        "b label": "b #c5c7d2",
        "light_blue": "#bbc8e8",
        "b white": "b #e9e9e9",
        "b highlight": "b #91abec",
        "b light_blue": "b #bbc8e8",
        "recording": "#ff5e5e",
        "b recording": "b #ff5e5e",
        "panel_border": "#6171a6",
        "table_border": "#333f62",
    }
)
TEXTUAL_THEME = TextualTheme(
    name="custom",
    primary="white",
    variables={
        "white": "#e9e9e9",
        "green": "#54efae",
        "yellow": "#f6ff8f",
        "dark_yellow": "#e6d733",
        "red": "#fd8383",
        "purple": "#b565f3",
        "dark_gray": "#969aad",
        "b_dark_gray": "b #969aad",
        "highlight": "#91abec",
        "label": "#c5c7d2",
        "b_label": "b #c5c7d2",
        "light_blue": "#bbc8e8",
        "b_white": "b #e9e9e9",
        "b_highlight": "b #91abec",
        "b_light_blue": "b #bbc8e8",
        "recording": "#ff5e5e",
        "b_recording": "b #ff5e5e",
        "panel_border": "#6171a6",
        "table_border": "#333f62",
    },
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
        self.initialized_flag = True if self.depl_mgr.is_initialized() else False
        self.pane_mgr = PaneMgr(
            config=config, catalogue=self.pane_catalogue, initialized_flag=self.initialized_flag)
        
        # Setup the themes
        theme = RICH_THEME
        self.console.push_theme(theme)
        self.console.set_window_title(self.TITLE)
        theme = TEXTUAL_THEME
        self.register_theme(theme)
        self.theme = "custom"

    def compose(self):
        self.topbar = TopBar(app_version=__version__)
        yield self.topbar
        yield Vertical(
            NavPane(initialized=self.initialized_flag),
            Clock()
        )
        yield self.pane_mgr

    ### Message handling happens here...

    # NavPane selections are routed here
    async def on_nav_leaf_selected(self, message: NavLeafSelected) -> None:
        category = message.parent
        instance = message.leaf
        if category == DEPLOYMENTS_LABEL and instance == DB4E_LABEL:
            db4e_data = self.depl_mgr.get_deployment(DB4E_FIELD)
            await self.pane_mgr.set_pane(name=DB4E_PANE, data=db4e_data)

    # Exit the app
    async def on_quit(self) -> None:
        self.exit()
    
    # Every form sends it's data here, we need to route the messages
    async def on_submit_form_data(self, message: SubmitFormData) -> None:
        module = message.form_data[TO_MODULE_FIELD]
        method = message.form_data[TO_METHOD_FIELD]
        results = await self.msg_router.dispatch(module, method, message.form_data)
        pane_name = self.msg_router.get_pane(module=module, method=method)
        await self.pane_mgr.set_pane(name=pane_name, data=results)

    # This is how the a pane is selected and loaded, including any data
    async def on_switch_pane(self, message: SwitchPane) -> None:
        await self.pane_mgr.set_pane(message.pane_name, message.data)

    # The individual Detail panes use this to update the TopBar
    async def on_update_top_bar(self, message: UpdateTopBar) -> None:
        self.topbar.set_state(title=message.title, sub_title=message.sub_title )

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