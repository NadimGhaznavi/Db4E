"""
db4e/recs/ops/BaseOps.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.BaseElem import BaseElem
from db4e.constants.DSQL import DCol


class BaseOps(BaseElem):
    """
    Base record for operational tracking entries.
    """

    def __init__(self, tracked_instance=None, tracked_type=None, rec=None):
        """
        Initialize the ops record and optionally hydrate from a DB record.

        :param tracked_instance: Optional instance identifier to track.
        :type tracked_instance: str or None
        :param tracked_type: Optional tracked type identifier.
        :type tracked_type: str or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__()
        self._tracked_type = tracked_type
        self._tracked_instance = tracked_instance
        self._updated_y = None
        self._updated_mo = None
        self._updated_d = None
        self._updated_h = None
        self._updated_mi = None
        self._updated_s = None
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
        self._tracked_instance = rec[DCol.TRACKED_INSTANCE]
        self._tracked_type = rec[DCol.TRACKED_TYPE]
        self._updated_y = rec[DCol.UPDATED_YEAR]
        self._updated_mo = rec[DCol.UPDATED_MONTH]
        self._updated_d = rec[DCol.UPDATED_DAY]
        self._updated_h = rec[DCol.UPDATED_HOUR]
        self._updated_mi = rec[DCol.UPDATED_MINUTE]
        self._updated_s = rec[DCol.UPDATED_SECOND]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with ops fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.TRACKED_INSTANCE: self._tracked_instance,
                DCol.TRACKED_TYPE: self._tracked_type,
            }
        )
        return data

    def tracked_instance(self, tracked_instance=None):
        """
        Get or set the tracked instance identifier.

        :param tracked_instance: Optional instance identifier to set.
        :type tracked_instance: str or None
        :return: Current tracked instance identifier.
        :rtype: str or None
        """
        if tracked_instance is not None:
            self._tracked_instance = tracked_instance
        return self._tracked_instance

    def tracked_type(self, tracked_type=None):
        """
        Get or set the tracked type identifier.

        :param tracked_type: Optional tracked type to set.
        :type tracked_type: str or None
        :return: Current tracked type identifier.
        :rtype: str or None
        """
        if tracked_type is not None:
            self._tracked_type = tracked_type
        return self._tracked_type

    def updated_year(self, updated_year=None):
        """
        Get or set the updated year.

        :param updated_year: Optional year value to set.
        :type updated_year: int or None
        :return: Current updated year.
        :rtype: int or None
        """
        if updated_year is not None:
            self._updated_y = updated_year
        return self._updated_y

    def updated_month(self, updated_month=None):
        """
        Get or set the updated month.

        :param updated_month: Optional month value to set.
        :type updated_month: int or None
        :return: Current updated month.
        :rtype: int or None
        """
        if updated_month is not None:
            self._updated_mo = updated_month
        return self._updated_mo

    def updated_day(self, updated_day=None):
        """
        Get or set the updated day.

        :param updated_day: Optional day value to set.
        :type updated_day: int or None
        :return: Current updated day.
        :rtype: int or None
        """
        if updated_day is not None:
            self._updated_d = updated_day
        return self._updated_d

    def updated_hour(self, updated_hour=None):
        """
        Get or set the updated hour.

        :param updated_hour: Optional hour value to set.
        :type updated_hour: int or None
        :return: Current updated hour.
        :rtype: int or None
        """
        if updated_hour is not None:
            self._updated_h = updated_hour
        return self._updated_h

    def updated_minute(self, updated_minute=None):
        """
        Get or set the updated minute.

        :param updated_minute: Optional minute value to set.
        :type updated_minute: int or None
        :return: Current updated minute.
        :rtype: int or None
        """
        if updated_minute is not None:
            self._updated_mi = updated_minute
        return self._updated_mi

    def updated_second(self, updated_second=None):
        """
        Get or set the updated second.

        :param updated_second: Optional second value to set.
        :type updated_second: int or None
        :return: Current updated second.
        :rtype: int or None
        """
        if updated_second is not None:
            self._updated_s = updated_second
        return self._updated_s
