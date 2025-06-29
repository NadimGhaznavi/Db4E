# db4e/Db4E.py

#   Database 4 Everything
#   Author: Nadim-Daniel Ghaznavi 
#   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/Db4E>
#   License: GPL 3.0

from textual.app import App
from db4e.Modules.ArgumentParser import Config

class Db4E:

    def __init__(self, config: Config, app: App) -> None:
        self.config = config
        self.app = app
        self.app_version = config.app_version
