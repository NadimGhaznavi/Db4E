"""
db4e/recs/mining/MinerHashrate.py

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


class MinerHashrate(BaseHourlyMining):
    """
    Record representing miner hashrate by pool and chain per hour.
    """

    def __init__(
        self, miner=None, pool=None, chain=None, hashrate=None, units=None, rec=None
    ):
        """
        Initialize the miner hashrate record and optionally hydrate from a DB record.

        :param miner: Optional miner identifier.
        :type miner: str or None
        :param pool: Optional pool identifier.
        :type pool: str or None
        :param chain: Optional chain identifier.
        :type chain: str or None
        :param hashrate: Optional hashrate value.
        :type hashrate: int or float or None
        :param units: Optional units for hashrate normalization.
        :type units: str or None
        :param rec: Optional database record mapping.
        :type rec: dict or None
        :return: None
        :rtype: None
        """
        super().__init__(rec=rec)
        self._miner = miner
        self._pool = pool
        self._chain = chain
        if hashrate is not None and units is not None:
            self._hashrate = normalize_hashrate(hashrate=hashrate, units=units)
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
        self._miner = rec[DCol.MINER]
        self._chain = rec[DCol.CHAIN]
        self._pool = rec[DCol.POOL]
        self._hashrate = rec[DCol.HASHRATE]

    def to_dict(self):
        """
        Return a dictionary representation of the record.

        :return: Dictionary with miner hashrate fields.
        :rtype: dict
        """
        data = super().to_dict()
        data.update(
            {
                DCol.MINER: self._miner,
                DCol.CHAIN: self._chain,
                DCol.POOL: self._pool,
                DCol.HASHRATE: self._hashrate,
            }
        )
        return data

    def chain(self, chain=None):
        """
        Get or set the chain identifier.

        :param chain: Optional chain identifier to set.
        :type chain: str or None
        :return: Current chain identifier.
        :rtype: str or None
        """
        if chain is not None:
            self._chain = chain
        return self._chain

    def hashrate(self, hashrate=None):
        """
        Get or set the hashrate value.

        :param hashrate: Optional hashrate value to set.
        :type hashrate: int or float or None
        :return: Current hashrate value.
        :rtype: int or float or None
        """
        if hashrate is not None:
            self._hashrate = hashrate
        return self._hashrate

    def miner(self, miner=None):
        """
        Get or set the miner identifier.

        :param miner: Optional miner identifier to set.
        :type miner: str or None
        :return: Current miner identifier.
        :rtype: str or None
        """
        if miner is not None:
            self._miner = miner
        return self._miner

    def pool(self, pool=None):
        """
        Get or set the pool identifier.

        :param pool: Optional pool identifier to set.
        :type pool: str or None
        :return: Current pool identifier.
        :rtype: str or None
        """
        if pool is not None:
            self._pool = pool
        return self._pool

    def constraints(self):
        """
        Return the uniqueness constraint columns for this record.

        :return: Column names defining uniqueness.
        :rtype: list
        """
        return [
            DCol.MINER,
            DCol.CHAIN,
            DCol.POOL,
            DCol.UPDATED_YEAR,
            DCol.UPDATED_MONTH,
            DCol.UPDATED_DAY,
            DCol.UPDATED_HOUR,
        ]
