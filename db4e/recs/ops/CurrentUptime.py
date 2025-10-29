"""
db4e/recs/ops/CurrentUptime.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.ops.BaseUptime import BaseUptime
from db4e.constants.DSQL import DCol


class CurrentUptime(BaseUptime):
    """A class to encapsulate the current uptime of a component"""

    def __init__(self, tracked_type=None, tracked_instance=None, rec=None):
        super().__init__(tracked_type=tracked_type, tracked_instance=tracked_instance)

        if rec:
            self.from_rec(rec)
