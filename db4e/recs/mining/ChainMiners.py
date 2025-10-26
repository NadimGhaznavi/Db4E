"""
db4e/recs/mining/ChainMiners.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseHourlyMining import BaseHourlyMining
from db4e.constants.DSQL import DCol


class ChainMiners(BaseHourlyMining):

    def __init__(self, chain=None, num_miners=None, rec=None):
        super().__init__(rec=rec)
        self._chain = chain
        self._miners = num_miners
        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._chain = rec[DCol.CHAIN]
        self._miners = rec[DCol.MINERS]

    def to_dict(self):
        data = super().to_dict()
        data.update({DCol.CHAIN: self._chain, DCol.MINERS: self._miners})
        return data

    def constraints(self):
        return [
            DCol.CHAIN,
            DCol.UPDATED_YEAR,
            DCol.UPDATED_MONTH,
            DCol.UPDATED_DAY,
            DCol.UPDATED_HOUR,
        ]
