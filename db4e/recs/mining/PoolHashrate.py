"""
db4e/recs/mining/PoolHashrate.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    Website: https://db4e.osoyalce.com/
    License: GPL 3.0
"""

from db4e.recs.mining.BaseHourlyMining import BaseHourlyMining
from db4e.util.Helper import normalize_hashrate
from db4e.constants.DSQL import DCol


class PoolHashrate(BaseHourlyMining):

    def __init__(self, pool=None, chain=None, hashrate=None, units=None, rec=None):
        super().__init__(rec=rec)
        self._pool = pool
        self._chain = chain
        self._hashrate = hashrate
        if hashrate is not None and units is not None:
            self._hashrate = normalize_hashrate(hashrate=hashrate, units=units)
        if rec:
            self.from_rec(rec)

    def from_rec(self, rec):
        super().from_rec(rec)
        self._pool = rec[DCol.POOL]
        self._chain = rec[DCol.CHAIN]
        self._hashrate = rec[DCol.HASHRATE]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                DCol.POOL: self._pool,
                DCol.CHAIN: self._chain,
                DCol.HASHRATE: self._hashrate,
            }
        )
        return data

    def pool(self, pool=None):
        if pool is not None:
            self._pool = pool
        return self._pool

    def chain(self, chain=None):
        if chain is not None:
            self._chain = chain
        return self._chain

    def hashrate(self, hashrate=None):
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    def constraints(self):
        return [
            DCol.POOL,
            DCol.CHAIN,
            DCol.UPDATED_YEAR,
            DCol.UPDATED_MONTH,
            DCol.UPDATED_DAY,
            DCol.UPDATED_HOUR,
        ]
