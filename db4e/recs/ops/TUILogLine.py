"""
db4e/db/OpsRecs.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.BaseElem import BaseElem
from db4e.constants.DSQL import DCol


class TUILogLine(BaseElem):
    """A class to encapsulate a console log messages"""

    def __init__(
        self,
        tracked_instance=None,
        tracked_type=None,
        op=None,
        status=None,
        msg=None,
        details=None,
        rec=None,
    ):
        super().__init__(tracked_instance=tracked_instance, tracked_type=tracked_type)
        self._status = status
        self._operation = op
        self._message = msg
        self._details = details
        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._status = rec[DCol.STATUS]
        self._operation = rec[DCol.OPERATION]
        self._message = rec[DCol.MESSAGE]
        self._details = rec[DCol.DETAILS]

    def to_dict(self):
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
        if status is not None:
            self._status = status
        return self._status

    def operation(self, operation=None):
        if operation is not None:
            self._operation = operation
        return self._operation

    def message(self, message=None):
        if message is not None:
            self._message = message
        return self._message

    def details(self, details=None):
        if details is not None:
            self._details = details
        return self._details
