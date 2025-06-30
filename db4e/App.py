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
from loguru import logger
from rich.theme import Theme as RichTheme
from textual.app import App
from textual.command import Provider
from textual.containers import Horizontal, Vertical
from textual.theme import Theme as TextualTheme
from textual.widgets import Tabs
from rich.traceback import Traceback
from db4e.Modules.ArgumentParser import Config, create_config_from_args
from db4e.Modules.CommandManager import CommandManager
from db4e.Modules.TabManager import TabManager
from db4e.Modules.Db4eScreen import Db4eScreen
from db4e.Widgets.TopBar import TopBar

try:
    __package_name__ = metadata.metadata(__package__ or __name__)["Name"]
    __version__ = metadata.version(__package__ or __name__)
except Exception:
    __package_name__ = "Db4E"
    __version__ = "N/A"


class CommandPaletteCommands(Provider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db4e_app: Db4EApp = self.db4e_app

    def async_command(self, key: str):
        """Helper function to call the process_key_event command asynchronously."""
        self.app.call_later(self.db4e_app.process_key_event, key)

    def get_command_hits(self):
        """Helper function to get all commands and format them for discovery or search."""
        return
    
    async def discover(self):
        return
    
    async def search(self, query: str):
        return

class Db4EApp(App):
    TITLE = "Db4E"
    CSS_PATH = "Db4E.tcss"
    COMMANDS = {CommandPaletteCommands}
    COMMAND_PALETTE_BINDING = "question_mark"

    def __init__(self, config: Config):
        super().__init__()

        self.config = config
        self.command_manager = CommandManager()

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

        if config.daemon_mode:
            logger.info(
                f"Starting Db4E v{__version__} in daemon mode with a refresh "
                f"interval of {config.refresh_interval}s"
            )
            logger.info(f"Log file: {config.daemon_mode_log_file}")

    async def on_mount(self):
        self.tab_manager = TabManager(app=self.app, config=self.config)
        await self.tab_manager.create_ui_widgets()
        tab = await self.tab_manager.create_tab(tab_name="Initial Tab")
        self.tab_manager.setup_component_tab(tab)
        self.tab_manager.run_component_updater(tab)

        if not self.config.daemon_mode:
            self.tab_manager.run_metrics_collector(tab)

    def compose(self):
        yield TopBar(component="", app_version=__version__, help="press [b highlight]?[/b highlight] for commands")
        yield Tabs(id="host_tabs")

    def on_ready(self) -> None:
        self.push_screen(Db4eScreen())

    def _handle_exception(self, error: Exception) -> None:
        self.bell()
        self.exit(message=Traceback(show_locals=True, width=None, locals_max_length=5))


def setup_logger(config: Config):
    logger.remove()

    # If we're not using daemon mode, we want to essentially disable logging
    if not config.daemon_mode:
        return

    logger.level("DEBUG", color="<magenta>")
    logger.level("INFO", color="<blue>")
    logger.level("WARNING", color="<yellow>")
    logger.level("ERROR", color="<red>")
    log_format = "<dim>{time:MM-DD-YYYY HH:mm:ss}</dim> <b><level>[{level}]</level></b> {message}"
    log_level = "INFO"

    # Add terminal & file logging
    logger.add(sys.stdout, format=log_format, backtrace=True, colorize=True, level=log_level)
    logger.add(config.daemon_mode_log_file, format=log_format, backtrace=True, level=log_level)

    # Exit when critical is used
    logger.add(lambda _: sys.exit(1), level="CRITICAL")

def main():
    # Set environment variables for better color support
    os.environ["TERM"] = "xterm-256color"
    os.environ["COLORTERM"] = "truecolor"

    config = create_config_from_args(__version__)
    setup_logger(config)

    setup_logger(config)
    app = Db4EApp(config)
    app.run()


if __name__ == "__main__":
    main()