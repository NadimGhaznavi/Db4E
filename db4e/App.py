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
from textual import events
from textual.app import App
from textual.theme import Theme as TextualTheme
from rich.theme import Theme as RichTheme
from rich.traceback import Traceback

try:
    __package_name__ = metadata.metadata(__package__ or __name__)["Name"]
    __version__ = metadata.version(__package__ or __name__)
except Exception:
    __package_name__ = "Db4E"
    __version__ = "N/A"


from functools import partial
from textual.command import Provider
from db4e.Widgets.TopBar import TopBar
from db4e.Widgets.Clock import Clock
from db4e.Widgets.DetailPane import DetailPane
from db4e.Widgets.NavPane import NavPane
from db4e.Modules.ArgumentParser import get_cli_args, Config

class Db4EApp(App):
    TITLE = "Db4E"
    CSS_PATH = "Db4E.tcss"

    def __init__(self, ini: Config, **kwargs):
        super().__init__(**kwargs)
        self.ini = ini
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

        if ini.config['op'] == 'run_daemon':
            refresh_interval = ini.config['refresh_interval']
            log_file = ini.config['service_log_file']
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
        yield TopBar(component="", app_version=__version__)
        yield NavPane()
        yield DetailPane()
        yield Clock()

    def _handle_exception(self, error: Exception) -> None:
        self.bell()
        self.exit(message=Traceback(show_locals=True, width=None, locals_max_length=5))

def setup_logger(ini: Config):
    logger.remove()

    # If we're not using daemon mode, we want to essentially disable logging
    if not ini.config['op'] == 'run_daemon':
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

    config = get_cli_args(__version__)
    setup_logger(config)
    app = Db4EApp(config)
    app.run()


if __name__ == "__main__":
    main()