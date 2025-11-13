"""
db4e/elem/monero/LocalMonero.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.monero.BaseMonero import BaseMonero
from db4e.constants.DSQL import DCol


class LocalMonero(BaseMonero):
    def __init__(self, rec=None):
        super().__init__()
        self._enabled = False
        if rec is not None:
            self.from_rec(rec)

    def __repr__(self):
        return f"{self.elem_type()}({self.instance()})"

    def from_rec(self, rec):
        super().from_rec(rec)
        self._enabled = rec[DCol.ENABLED]

    def to_dict(self):
        data = super().to_dict()
        data.update({DCol.ENABLED: self._enabled})
        return data

    def enabled(self, enabled=None):
        if enabled is not None:
            self._enabled = enabled
        return self._enabled
