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
    """
    Record representing the total uptime of a tracked component.
    """

    def __init__(
        self, tracked_type=None, tracked_instance=None, uptime_secs=None, rec=None
    ):
        """
        Initialize the total uptime record and optionally hydrate from a DB record.

        :param tracked_type: Optional tracked type identifier.
        :type tracked_type: str or None
        :param tracked_instance: Optional tracked instance identifier.
        :type tracked_instance: str or None
        :param uptime_secs: Optional initial uptime value.
        :type uptime_secs: int or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(tracked_type=tracked_type, tracked_instance=tracked_instance)
        self._uptime_secs = uptime_secs or 0

        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        """
        Populate the object from a database record.

        :param rec: Database record mapping.
        :type rec: dict
        :return: None
        :rtype: None
        """
        super().from_rec(rec)
        self._uptime_secs = rec[DCol.UPTIME_SECS]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with total uptime fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.UPTIME_SECS: self._uptime_secs,
            }
        )
        return data

    def uptime_secs(self, secs=None):
        """
        Get or set the uptime in seconds.

        :param secs: Optional uptime seconds to set.
        :type secs: int or None
        :return: Uptime in seconds.
        :rtype: int
        """
        if not secs:
            return self._uptime_secs
        self._uptime_secs = secs
        return self._uptime_secs
