"""
db4e/Modules/PaneManager.py

   Database 4 Everything
   Author: Nadim-Daniel Ghaznavi 
   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
   License: GPL 3.0
"""

from db4e.Panes.Welcome import Welcome

class PaneManager:

    def get_pane(self, pane_name):
        print(f'PaneManager:get_pane({pane_name})')
        if pane_name == 'Welcome':
            return Welcome(id=pane_name)