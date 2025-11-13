"""
db4e/elem/BaseElem.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.constants.DSQL import DCol


class BaseElem:
    def __init__(self, rec=None):
        self._id = None
        if rec is not None:
            self.from_rec(rec)

    def __repr__(self):
        return self.elem_type()

    def from_rec(self, rec):
        self._id = rec[DCol.ID]

    def to_dict(self):
        return {DCol.ID: self._id}

    def elem_type(self):
        return type(self).__name__

    def id(self, id=None):
        if id is not None:
            self._id = id
        return self._id
