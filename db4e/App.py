#!/usr/bin/env python3

# db4e/App.py

#   Database 4 Everything
#   Author: Nadim-Daniel Ghaznavi 
#   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#   License: GPL 3.0

import os
import sys
from dataclasses import dataclass, field, fields
from importlib import metadata
from textual import events
from textual.app import App
from textual.theme import Theme as TextualTheme
from textual.widgets import Footer
from textual.message import Message
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
from db4e.Panes.Welcome import Welcome
from db4e.Panes.InitialSetup import InitialSetup
from db4e.Messages.SubmitFormData import SubmitFormData

class Db4EApp(App):
    TITLE = "Db4E"
    CSS_PATH = "Db4E.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self, ini: Config, **kwargs):
        super().__init__(**kwargs)
        self.ini = ini
        self.deployment_mgr = DeploymentMgr(ini)
        theme = RichTheme(
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
        self.console.push_theme(theme)
        self.console.set_window_title(self.TITLE)
        theme = TextualTheme(
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
        self.register_theme(theme)
        self.theme = "custom"

        if ini.config['db4e']['op'] == 'run_daemon':
            refresh_interval = ini.config['db4e']['refresh_interval']
            log_file = ini.config['db4e']['service_log_file']
            logger.info(
                f"Starting Db4E v{__version__} in daemon mode with a refresh "
                f"interval of {refresh_interval}s"
            )
            logger.info(f"Log file: {log_file}")

    async def on_key(self, event: events.Key):
        if len(self.screen_stack) > 1:
            return

        await self.process_key_event(event.key)

    async def process_key_event(self, key):
        if key == "q":
            self.app.exit()

    def compose(self):
        self.topbar = TopBar(app_version=__version__)
        initialized_flag = self.deployment_mgr.is_initialized()
        yield self.topbar
        yield NavPane(initialized=initialized_flag)
        yield DetailPane(initialized=initialized_flag)
        yield Clock()
        yield Footer()

    ### App.py is the message hub

    #async def on_message(self, message: Message) -> None:
    async def on_submit_form(self, message: SubmitFormData) -> None:
        results = await self.deployment_mgr.initial_setup(message.form_data)

    # Panes updating the TopBar...
    def on_welcome_update_top_bar(self, message: Welcome.UpdateTopBar):
        self.update_topbar(message.component, message.msg)
    def on_initial_setup_update_top_bar(self, message: InitialSetup.UpdateTopBar):
        self.update_topbar(message.component, message.msg)
    # TopBar update
    def update_topbar(self, component: str, message: str) -> None:
        if self.topbar:
            self.topbar.set_component(component)
            self.topbar.set_msg(message)

    def _handle_exception(self, error: Exception) -> None:
        self.bell()
        self.exit(message=Traceback(show_locals=True, width=None, locals_max_length=5))

def main():
    # Set environment variables for better color support
    os.environ["TERM"] = "xterm-256color"
    os.environ["COLORTERM"] = "truecolor"

    config_manager = ConfigMgr(__version__)
    config = config_manager.get_config()
    app = Db4EApp(config)
    app.run()


if __name__ == "__main__":
    main()