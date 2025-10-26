"""
db4e/recs/mining/BaseHourlyMining.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseMining import BaseMining
from db4e.constants.DSQL import DCol


class ShareFoundEvent(BaseMining):

    def __init__(self, miner=None, chain=None, pool=None, effort=None, rec=None):
        super().__init__(rec=rec)
        self._miner = miner
        self._chain = chain
        self._pool = pool
        self._effort = effort
        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._miner = rec[DCol.MINER]
        self._chain = rec[DCol.CHAIN]
        self._pool = rec[DCol.POOL]
        self._effort = rec[DCol.EFFORT]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                DCol.MINER: self._miner,
                DCol.CHAIN: self._chain,
                DCol.POOL: self._pool,
                DCol.EFFORT: self._effort,
            }
        )
        return data

    def miner(self, miner=None):
        if miner is not None:
            self._miner = miner
        return self._miner

    def chain(self, chain=None):
        if chain is not None:
            self._chain = chain
        return self._chain

    def pool(self, pool=None):
        if pool is not None:
            self._pool = pool
        return self._pool

    def effort(self, effort=None):
        if effort is not None:
            self._effort = effort
        return self._effort
