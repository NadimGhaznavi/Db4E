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

    def check_for_new_version(self):
        # Query PyPI API to get the latest version
        try:
            url = self.config.pypi_repository
            response = requests.get(url, timeout=3)

            if response.status_code == 200:
                data = response.json()

                # Extract the latest version from the response
                latest_version = data["info"]["version"]

                # Compare the current version with the latest version
                if parse_version(latest_version) > parse_version(__version__):
                    self.notify(
                        f"{Emoji('tada')}  [b]New version [$highlight]{latest_version}[/$highlight] is available![/b] "
                        f"{Emoji('tada')}\n\nPlease update at your earliest convenience\n"
                        f"[$dark_gray]Find more details at https://github.com/NadimGhaznavi/db4e",
                        title="",
                        severity="information",
                        timeout=20,
                    )

                    logger.warning(
                        f"New version {latest_version} is available! Please update at your earliest convenience. "
                        "Find more details at https://github.com/NadimGhaznavi/db4e"
                    )
        except Exception:
            pass

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

    setup_logger(arg_parser.config)

    app = Db4EApp()
    app.run()


if __name__ == "__main__":
    main()