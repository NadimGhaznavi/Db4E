"""
db4e/db/OpsRecs.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.ops.BaseOps import BaseOps
from db4e.constants.DSQL import DCol


class TUILogLine(BaseOps):
    """
    Record representing a console log message.
    """

    def __init__(
        self,
        tracked_instance=None,
        tracked_type=None,
        operation=None,
        status=None,
        message=None,
        details=None,
        rec=None,
    ):
        """
        Initialize the log line record and optionally hydrate from a DB record.

        :param tracked_instance: Optional tracked instance identifier.
        :type tracked_instance: str or None
        :param tracked_type: Optional tracked type identifier.
        :type tracked_type: str or None
        :param operation: Optional operation label.
        :type operation: str or None
        :param status: Optional status value.
        :type status: str or None
        :param message: Optional log message.
        :type message: str or None
        :param details: Optional detail payload.
        :type details: str or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(tracked_instance=tracked_instance, tracked_type=tracked_type)
        self._status = status
        self._operation = operation
        self._message = message
        self._details = details
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
        self._status = rec[DCol.STATUS]
        self._operation = rec[DCol.OPERATION]
        self._message = rec[DCol.MESSAGE]
        self._details = rec[DCol.DETAILS]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with log line fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.STATUS: self._status,
                DCol.OPERATION: self._operation,
                DCol.MESSAGE: self._message,
                DCol.DETAILS: self._details,
            }
        )
        return data

    def status(self, status=None):
        """
        Get or set the status value.

        :param status: Optional status value to set.
        :type status: str or None
        :return: Current status value.
        :rtype: str or None
        """
        if status is not None:
            self._status = status
        return self._status

    def operation(self, operation=None):
        """
        Get or set the operation label.

        :param operation: Optional operation label to set.
        :type operation: str or None
        :return: Current operation label.
        :rtype: str or None
        """
        if operation is not None:
            self._operation = operation
        return self._operation

    def message(self, message=None):
        """
        Get or set the log message.

        :param message: Optional log message to set.
        :type message: str or None
        :return: Current log message.
        :rtype: str or None
        """
        if message is not None:
            self._message = message
        return self._message

    def details(self, details=None):
        """
        Get or set the log detail payload.

        :param details: Optional detail payload to set.
        :type details: str or None
        :return: Current detail payload.
        :rtype: str or None
        """
        if details is not None:
            self._details = details
        return self._details

    # Timestamp fields
    def updated_year(self, updated_y=None):
        """
        Get or set the updated year.

        :param updated_y: Optional year value to set.
        :type updated_y: int or None
        :return: Current updated year.
        :rtype: int or None
        """
        if updated_y is not None:
            self._updated_y = updated_y
        return self._updated_y

    def updated_month(self, updated_mo=None):
        """
        Get or set the updated month.

        :param updated_mo: Optional month value to set.
        :type updated_mo: int or None
        :return: Current updated month.
        :rtype: int or None
        """
        if updated_mo is not None:
            self._updated_mo = updated_mo
        return self._updated_mo

    def updated_day(self, updated_d=None):
        """
        Get or set the updated day.

        :param updated_d: Optional day value to set.
        :type updated_d: int or None
        :return: Current updated day.
        :rtype: int or None
        """
        if updated_d is not None:
            self._updated_d = updated_d
        return self._updated_d

    def updated_hour(self, updated_h=None):
        """
        Get or set the updated hour.

        :param updated_h: Optional hour value to set.
        :type updated_h: int or None
        :return: Current updated hour.
        :rtype: int or None
        """
        if updated_h is not None:
            self._updated_h = updated_h
        return self._updated_h

    def updated_minute(self, updated_mi=None):
        """
        Get or set the updated minute.

        :param updated_mi: Optional minute value to set.
        :type updated_mi: int or None
        :return: Current updated minute.
        :rtype: int or None
        """
        if updated_mi is not None:
            self._updated_mi = updated_mi
        return self._updated_mi

    def updated_second(self, updated_s=None):
        """
        Get or set the updated second.

        :param updated_s: Optional second value to set.
        :type updated_s: int or None
        :return: Current updated second.
        :rtype: int or None
        """
        if updated_s is not None:
            self._updated_s = updated_s
        return self._updated_s
