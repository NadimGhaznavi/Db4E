# db4e/Modules/PaneManager.py
#
#   Database 4 Everything
#   Author: Nadim-Daniel Ghaznavi 
#   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#   License: GPL 3.0import argparse

from db4e.Panes.Welcome import Welcome

class PaneManager:

    def get_pane(self, pane_name):
        if pane_name == 'Welcome':
            return Welcome()