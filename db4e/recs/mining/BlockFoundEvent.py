"""
db4e/recs/mining/BlockFoundEvent.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseMining import BaseMining
from db4e.constants.DSQL import DCol


class BlockFoundEvent(BaseMining):

    def __init__(self, chain=None, rec=None):
        super().__init__(rec=rec)
        self._chain = chain
        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._chain = rec[DCol.CHAIN]

    def to_dict(self):
        data = super().to_dict()
        data.update({DCol.CHAIN: self._chain})
        return data

    def chain(self, chain=None):
        if chain is not None:
            self._chain = chain
        return self._chain
