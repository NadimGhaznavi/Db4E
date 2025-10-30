"""
db4e/recs/ops/CurrentUptime.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.ops.BaseOps import BaseOps
from db4e.constants.DSQL import DCol


class CurrentUptime(BaseOps):
    """A class to encapsulate the current uptime of a component"""

    def __init__(self, tracked_type=None, tracked_instance=None, rec=None):
        super().__init__(tracked_type=tracked_type, tracked_instance=tracked_instance)
        self._cur_time = None
        self._start_time = None
        self._stop_time = None
        self._uptime_secs = 0

        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._cur_time = rec[DCol.CUR_TIME]
        self._start_time = rec[DCol.START_TIME]
        self._stop_time = rec[DCol.STOP_TIME]
        self._uptime_secs = rec[DCol.UPTIME_SECS]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                DCol.CUR_TIME: self._cur_time,
                DCol.START_TIME: self._start_time,
                DCol.STOP_TIME: self._stop_time,
                DCol.UPTIME_SECS: self._uptime_secs,
            }
        )
        return data

    def cur_time(self, cur_time=None):
        if cur_time is not None:
            self._cur_time = cur_time
        return self._cur_time

    def start_time(self, start_time=None):
        if start_time is not None:
            self._start_time = start_time
        return self._start_time

    def stop_time(self, stop_time=None):
        if stop_time is not None:
            self._stop_time = stop_time
        return self._stop_time

    def uptime_secs(self, secs=None):
        if not secs:
            return self._uptime_secs
        self._uptime_secs = secs
        return self._uptime_secs
