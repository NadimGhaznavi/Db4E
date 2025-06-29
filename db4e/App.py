#!/usr/bin/env python3

# db4e/App.py

#   Database 4 Everything
#   Author: Nadim-Daniel Ghaznavi 
#   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#   License: GPL 3.0

import argparse
import json
import os
import sys
import re
from configparser import RawConfigParser
from dataclasses import dataclass, field, fields
from typing import Dict, List
from urllib.parse import ParseResult, urlparse

from importlib import metadata

from loguru import logger

from rich.theme import Theme as RichTheme
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.theme import Theme as TextualTheme
from textual.command import DiscoveryHit, Hit, Provider

from db4e.Db4E import Db4E
from db4e.Modules.ArgumentParser import ArgumentParser, Config
from db4e.Modules.CommandManager import CommandManager

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

        if self.config.hostgroup:
            self.connect_as_hostgroup(self.config.hostgroup)
        else:
            tab = await self.tab_manager.create_tab(tab_name="Initial Tab")

            if self.config.tab_setup:
                self.tab_manager.setup_host_tab(tab)
            elif self.tab_manager.active_tab.dolphie.replay_file:
                self.tab_manager.active_tab.replay_manager = ReplayManager(tab.dolphie)
                if not tab.replay_manager.verify_replay_file():
                    tab.replay_manager = None
                    self.tab_manager.setup_host_tab(tab)
                    return

                self.tab_manager.rename_tab(tab)
                self.tab_manager.update_connection_status(tab=tab, connection_status=ConnectionStatus.connected)
                self.run_worker_replay(self.tab_manager.active_tab.id)
            else:
                self.run_worker_main(self.tab_manager.active_tab.id)

                if not self.config.daemon_mode:
                    self.run_worker_replicas(self.tab_manager.active_tab.id)

    def compose(self):
        yield TopBar(host="", app_version=__version__, help="press [b highlight]?[/b highlight] for commands")
        yield Tabs(id="host_tabs")

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

    arg_parser = ArgumentParser(__version__)
    parsed_config = arg_parser.get_config()
    config = Config(app_version=__version__)
    setup_logger(config)

    setup_logger(config)
    app = Db4EApp(config)
    app.run()


if __name__ == "__main__":
    main()