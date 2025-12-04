"""
db4e/recs/ops/TotalUptime.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.ops.BaseOps import BaseOps
from db4e.constants.DSQL import DCol


class TotalUptime(BaseOps):
    """A class to encapsulate the total uptime of a component"""

    def __init__(
        self, tracked_type=None, tracked_instance=None, uptime_secs=None, rec=None
    ):
        super().__init__(tracked_type=tracked_type, tracked_instance=tracked_instance)
        self._uptime_secs = uptime_secs or 0

        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._uptime_secs = rec[DCol.UPTIME_SECS]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                DCol.UPTIME_SECS: self._uptime_secs,
            }
        )
        return data

    def uptime_secs(self, secs=None):
        if not secs:
            return self._uptime_secs
        self._uptime_secs = secs
        return self._uptime_secs
