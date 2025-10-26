"""
db4e/recs/monero/BaseMonero.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.BaseElem import BaseElem
from db4e.constants.DSQL import DCol


class BaseMonero(BaseElem):

    def __init__(self, rec=None):
        super().__init__()
        self._instance = None
        self._updated_y = None
        self._updated_mo = None
        self._updated_d = None
        self._updated_h = None
        self._updated_mi = None
        self._updated_s = None
        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._instance = rec[DCol.INSTANCE]
        self._updated_y = rec[DCol.UPDATED_YEAR]
        self._updated_mo = rec[DCol.UPDATED_MONTH]
        self._updated_d = rec[DCol.UPDATED_DAY]
        self._updated_h = rec[DCol.UPDATED_HOUR]
        self._updated_mi = rec[DCol.UPDATED_MINUTE]
        self._updated_s = rec[DCol.UPDATED_SECOND]

    def to_dict(self):
        data = super().to_dict()
        data.update({DCol.INSTANCE: self._instance})
        return data

    def instance(self, instance=None):
        if instance is not None:
            self._instance = instance
        return self._instance
